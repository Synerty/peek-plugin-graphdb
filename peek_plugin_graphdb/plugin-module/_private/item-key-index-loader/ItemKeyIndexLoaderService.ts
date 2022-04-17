import { Observable, Subject } from "rxjs";
import { filter, first, takeUntil } from "rxjs/operators";
import { Injectable } from "@angular/core";
import {
    extend,
    NgLifeCycleEvents,
    Payload,
    PayloadEnvelope,
    TupleOfflineStorageNameService,
    TupleOfflineStorageService,
    TupleSelector,
    TupleStorageFactoryService,
    VortexService,
    VortexStatusService,
} from "@synerty/vortexjs";

import {
    graphDbCacheStorageName,
    graphDbFilt,
    graphDbTuplePrefix,
} from "../PluginNames";
import { ItemKeyIndexEncodedChunkTuple } from "./ItemKeyIndexEncodedChunkTuple";
import { ItemKeyIndexUpdateDateTuple } from "./ItemKeyIndexUpdateDateTuple";
import { ItemKeyTuple } from "./ItemKeyTuple";
import { ItemKeyIndexLoaderStatusTuple } from "./ItemKeyIndexLoaderStatusTuple";
import { GraphDbModelSetTuple } from "../../GraphDbModelSetTuple";
import { GraphDbTupleService } from "../GraphDbTupleService";
import { GraphDbPackedItemKeyTuple } from "./GraphDbPackedItemKeyTuple";
import {
    DeviceOfflineCacheControllerService,
    OfflineCacheStatusTuple,
} from "@peek/peek_core_device";

// ----------------------------------------------------------------------------

let clientItemKeyIndexWatchUpdateFromDeviceFilt = extend(
    { key: "clientItemKeyIndexWatchUpdateFromDevice" },
    graphDbFilt
);

const cacheAll = "cacheAll";

// ----------------------------------------------------------------------------
/** ItemKeyIndexChunkTupleSelector
 *
 * This is just a short cut for the tuple selector
 */

class ItemKeyIndexChunkTupleSelector extends TupleSelector {
    constructor(private chunkKey: string) {
        super(graphDbTuplePrefix + "ItemKeyIndexChunkTuple", { key: chunkKey });
    }

    toOrderedJsonStr(): string {
        return this.chunkKey;
    }
}

// ----------------------------------------------------------------------------
/** UpdateDateTupleSelector
 *
 * This is just a short cut for the tuple selector
 */
class UpdateDateTupleSelector extends TupleSelector {
    constructor() {
        super(ItemKeyIndexUpdateDateTuple.tupleName, {});
    }
}

// ----------------------------------------------------------------------------
/** hash method
 */
let BUCKET_COUNT = 8192;

function keyChunk(modelSetKey: string, key: string): string {
    /** Object ID Chunk
     
     This method creates an int from 0 to MAX, representing the hash bucket for this
     object Id.
     
     This is simple, and provides a reasonable distribution
     
     @param modelSetKey: The key of the model set that the itemKeyIndexs are in
     @param key: The key of the itemKeyIndex to get the chunk key for
     
     @return: The bucket / chunkKey where you'll find the object with this ID
     
     */
    if (key == null || key.length == 0)
        throw new Error("key is None or zero length");

    let bucket = 0;

    for (let i = 0; i < key.length; i++) {
        bucket = (bucket << 5) - bucket + key.charCodeAt(i);
        bucket |= 0; // Convert to 32bit integer
    }

    bucket = bucket & (BUCKET_COUNT - 1);

    return `${modelSetKey}.${bucket}`;
}

// ----------------------------------------------------------------------------
/** ItemKeyIndex Cache
 *
 * This class has the following responsibilities:
 *
 * 1) Maintain a local storage of the index
 *
 * 2) Return DispKey graphdb based on the index.
 *
 */
@Injectable()
export class ItemKeyIndexLoaderService extends NgLifeCycleEvents {
    private UPDATE_CHUNK_FETCH_SIZE = 32;
    private OFFLINE_CHECK_PERIOD_MS = 15 * 60 * 1000; // 15 minutes

    private index = new ItemKeyIndexUpdateDateTuple();
    private askServerChunks: ItemKeyIndexUpdateDateTuple[] = [];

    private _hasLoaded = false;

    private _hasLoadedSubject = new Subject<void>();
    private storage: TupleOfflineStorageService;

    private _statusSubject = new Subject<ItemKeyIndexLoaderStatusTuple>();
    private _status = new ItemKeyIndexLoaderStatusTuple();

    private modelSetByIds: { [id: number]: GraphDbModelSetTuple } = {};
    private _hasModelSetLoaded = false;

    constructor(
        private vortexService: VortexService,
        private vortexStatusService: VortexStatusService,
        storageFactory: TupleStorageFactoryService,
        private tupleService: GraphDbTupleService,
        private deviceCacheControllerService: DeviceOfflineCacheControllerService
    ) {
        super();

        this.storage = new TupleOfflineStorageService(
            storageFactory,
            new TupleOfflineStorageNameService(
                graphDbCacheStorageName + ".item_key"
            )
        );

        this.setupVortexSubscriptions();
        this._notifyStatus();

        this.deviceCacheControllerService.triggerCachingObservable
            .pipe(takeUntil(this.onDestroyEvent))
            .pipe(filter((v) => v))
            .subscribe(() => {
                this.initialLoad();
                this._notifyStatus();
            });
    }

    isReady(): boolean {
        return this._hasLoaded;
    }

    isReadyObservable(): Observable<void> {
        return this._hasLoadedSubject;
    }

    statusObservable(): Observable<ItemKeyIndexLoaderStatusTuple> {
        return this._statusSubject;
    }

    status(): ItemKeyIndexLoaderStatusTuple {
        return this._status;
    }

    /** Get Segment Keys
     *
     * Get the objects with matching keywords from the index..
     *
     */
    getSegmentKeys(
        modelSetKey: string,
        key: string,
        itemType: number = ItemKeyTuple.ITEM_TYPE_VERTEX
    ): Promise<string[]> {
        return this.getItemKeys(modelSetKey, [key]).then(
            (tuples: ItemKeyTuple[]) => {
                let keys = [];
                for (let tuple of tuples) {
                    // if (tuple.itemType == itemType) {
                    for (let segmentKey of tuple.segmentKeys) {
                        keys.push(segmentKey);
                    }
                    // }
                }
                return keys;
            }
        );
    }

    private _notifyReady(): void {
        if (this._hasModelSetLoaded && this._hasLoaded)
            this._hasLoadedSubject.next();
    }

    private _notifyStatus(): void {
        this._status.cacheForOfflineEnabled =
            this.deviceCacheControllerService.cachingEnabled;
        this._status.initialLoadComplete = this.index.initialLoadComplete;

        this._status.loadProgress = Object.keys(
            this.index.updateDateByChunkKey
        ).length;
        for (let chunk of this.askServerChunks)
            this._status.loadProgress -= Object.keys(
                chunk.updateDateByChunkKey
            ).length;

        this._statusSubject.next(this._status);

        const status = new OfflineCacheStatusTuple();
        status.pluginName = "peek_plugin_graphdb";
        status.indexName = "Key Index";
        status.loadingQueueCount = this._status.loadProgress;
        status.totalLoadedCount = this._status.loadTotal;
        status.lastCheckDate = new Date();
        status.initialFullLoadComplete = this._status.initialLoadComplete;
        this.deviceCacheControllerService.updateCachingStatus(status);
    }

    /** Initial load
     *
     * Load the dates of the index buckets and ask the server if it has any updates.
     */
    private initialLoad(): void {
        this.storage
            .loadTuples(new UpdateDateTupleSelector())
            .then((tuplesAny: any[]) => {
                let tuples: ItemKeyIndexUpdateDateTuple[] = tuplesAny;
                if (tuples.length != 0) {
                    this.index = tuples[0];

                    if (this.index.initialLoadComplete) {
                        this._hasLoaded = true;
                        this._notifyReady();
                    }
                }

                this.askServerForUpdates();
                this._notifyStatus();
            });

        this._notifyStatus();
    }

    private setupVortexSubscriptions(): void {
        // Services don't have destructors, I'm not sure how to unsubscribe.
        this.vortexService
            .createEndpointObservable(
                this,
                clientItemKeyIndexWatchUpdateFromDeviceFilt
            )
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((payloadEnvelope: PayloadEnvelope) => {
                this.processItemKeyIndexsFromServer(payloadEnvelope);
            });

        // If the vortex service comes back online, update the watch grids.
        this.vortexStatusService.isOnline
            .pipe(filter((isOnline) => isOnline == true))
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe(() => this.askServerForUpdates());
    }

    private areWeTalkingToTheServer(): boolean {
        return (
            this.deviceCacheControllerService.offlineModeEnabled &&
            this.vortexStatusService.snapshot.isOnline
        );
    }

    /** Ask Server For Updates
     *
     * Tell the server the state of the chunks in our index and ask if there
     * are updates.
     *
     */
    private askServerForUpdates() {
        if (!this.areWeTalkingToTheServer()) return;

        // If we're still caching, then exit
        if (this.askServerChunks.length != 0) {
            this.askServerForNextUpdateChunk();
            return;
        }

        this.tupleService.observer
            .pollForTuples(new UpdateDateTupleSelector())
            .then((tuplesAny: any) => {
                let serverIndex: ItemKeyIndexUpdateDateTuple = tuplesAny[0];
                let keys = Object.keys(serverIndex.updateDateByChunkKey);
                let keysNeedingUpdate: string[] = [];

                this._status.loadTotal = keys.length;

                // Tuples is an array of strings
                for (let chunkKey of keys) {
                    if (
                        !this.index.updateDateByChunkKey.hasOwnProperty(
                            chunkKey
                        )
                    ) {
                        this.index.updateDateByChunkKey[chunkKey] = null;
                        keysNeedingUpdate.push(chunkKey);
                    } else if (
                        this.index.updateDateByChunkKey[chunkKey] !=
                        serverIndex.updateDateByChunkKey[chunkKey]
                    ) {
                        keysNeedingUpdate.push(chunkKey);
                    }
                }
                this.queueChunksToAskServer(keysNeedingUpdate);
            });
    }

    /** Queue Chunks To Ask Server
     *
     */
    private queueChunksToAskServer(keysNeedingUpdate: string[]) {
        if (!this.areWeTalkingToTheServer()) return;

        this.askServerChunks = [];

        let count = 0;
        let indexChunk = new ItemKeyIndexUpdateDateTuple();

        for (let key of keysNeedingUpdate) {
            indexChunk.updateDateByChunkKey[key] =
                this.index.updateDateByChunkKey[key] || "";
            count++;

            if (count == this.UPDATE_CHUNK_FETCH_SIZE) {
                this.askServerChunks.push(indexChunk);
                count = 0;
                indexChunk = new ItemKeyIndexUpdateDateTuple();
            }
        }

        if (count) this.askServerChunks.push(indexChunk);

        this.askServerForNextUpdateChunk();

        this._status.lastCheck = new Date();
    }

    private askServerForNextUpdateChunk() {
        if (!this.areWeTalkingToTheServer()) return;

        if (this.askServerChunks.length == 0) return;

        let indexChunk: ItemKeyIndexUpdateDateTuple =
            this.askServerChunks.pop();
        let filt = extend({}, clientItemKeyIndexWatchUpdateFromDeviceFilt);
        filt[cacheAll] = true;
        let pl = new Payload(filt, [indexChunk]);
        this.vortexService.sendPayload(pl);

        this._status.lastCheck = new Date();
        this._notifyStatus();
    }

    /** Process ItemKeyIndexes From Server
     *
     * Process the grids the server has sent us.
     */
    private processItemKeyIndexsFromServer(payloadEnvelope: PayloadEnvelope) {
        if (payloadEnvelope.result != null && payloadEnvelope.result != true) {
            console.log(`ERROR: ${payloadEnvelope.result}`);
            return;
        }

        payloadEnvelope
            .decodePayload()
            .then((payload: Payload) => this.storeItemKeyIndexPayload(payload))
            .then(() => {
                if (this.askServerChunks.length == 0) {
                    this.index.initialLoadComplete = true;
                    this._hasLoaded = true;
                    this._hasLoadedSubject.next();
                } else if (payloadEnvelope.filt[cacheAll] == true) {
                    this.askServerForNextUpdateChunk();
                }
            })
            .then(() => this._notifyStatus())
            .catch(
                (e) =>
                    `ItemKeyIndexCache.processItemKeyIndexsFromServer failed: ${e}`
            );
    }

    private storeItemKeyIndexPayload(payload: Payload) {
        let tuplesToSave: ItemKeyIndexEncodedChunkTuple[] = <
            ItemKeyIndexEncodedChunkTuple[]
        >payload.tuples;
        if (tuplesToSave.length == 0) return;

        // 2) Store the index
        this.storeItemKeyIndexChunkTuples(tuplesToSave)
            .then(() => {
                // 3) Store the update date

                for (let graphDbIndex of tuplesToSave) {
                    this.index.updateDateByChunkKey[graphDbIndex.chunkKey] =
                        graphDbIndex.lastUpdate;
                }

                return this.storage.saveTuples(new UpdateDateTupleSelector(), [
                    this.index,
                ]);
            })
            .catch((e) =>
                console.log(`ItemKeyIndexCache.storeItemKeyIndexPayload: ${e}`)
            );
    }

    /** Store Index Bucket
     * Stores the index bucket in the local db.
     */
    private storeItemKeyIndexChunkTuples(
        encodedItemKeyIndexChunkTuples: ItemKeyIndexEncodedChunkTuple[]
    ): Promise<void> {
        let retPromise: any;
        retPromise = this.storage.transaction(true).then((tx) => {
            let promises = [];

            for (let encodedItemKeyIndexChunkTuple of encodedItemKeyIndexChunkTuples) {
                promises.push(
                    tx.saveTuplesEncoded(
                        new ItemKeyIndexChunkTupleSelector(
                            encodedItemKeyIndexChunkTuple.chunkKey
                        ),
                        encodedItemKeyIndexChunkTuple.encodedData
                    )
                );
            }

            return Promise.all(promises).then(() => tx.close());
        });
        return retPromise;
    }

    /** Get Segment Keys
     *
     * Get the objects with matching keywords from the index..
     *
     */
    private getItemKeys(
        modelSetKey: string,
        keys: string[]
    ): Promise<ItemKeyTuple[]> {
        if (modelSetKey == null || modelSetKey.length == 0) {
            Promise.reject("We've been passed a null/empty modelSetKey");
        }

        if (keys == null || keys.length == 0) {
            Promise.reject("We've been passed a null/empty keys");
        }

        // If there is no offline support, or we're online
        // This is never used at present.
        if (this.vortexStatusService.snapshot.isOnline) {
            let ts = new TupleSelector(GraphDbPackedItemKeyTuple.tupleName, {
                modelSetKey: modelSetKey,
                keys: keys,
            });

            let isOnlinePromise: any = this.vortexStatusService.snapshot
                .isOnline
                ? Promise.resolve()
                : this.vortexStatusService.isOnline
                      .pipe(filter((online) => online))
                      .pipe(first())
                      .toPromise();

            return isOnlinePromise
                .then(() =>
                    this.tupleService.offlineObserver.pollForTuples(ts, false)
                )
                .then((packedKeyIndexes: GraphDbPackedItemKeyTuple[]) => {
                    let itemKeys = [];
                    for (let packed of packedKeyIndexes) {
                        // Create the new object
                        let newObject = new ItemKeyTuple();
                        newObject.unpackJson(
                            packed.packedJson,
                            packed.key,
                            modelSetKey
                        );
                        itemKeys.push(newObject);
                    }
                    return itemKeys;
                });
        }

        if (!this.deviceCacheControllerService.offlineModeEnabled) {
            throw new Error(
                "Peek is not online," +
                    " and offline caching is not enabled" +
                    " or has not completed loading." +
                    " The ItemKeyIndex won't work."
            );
        }

        // If we do have offline support
        if (this.isReady()) return this.getItemKeysWhenReady(modelSetKey, keys);

        return this.isReadyObservable()
            .pipe(first())
            .toPromise()
            .then(() => this.getItemKeysWhenReady(modelSetKey, keys));
    }

    /** Get ItemKeyIndexs When Ready
     *
     * Get the objects with matching keywords from the index..
     *
     */
    private getItemKeysWhenReady(
        modelSetKey: string,
        keys: string[]
    ): Promise<ItemKeyTuple[]> {
        let keysByChunkKey: { [key: string]: string[] } = {};
        let chunkKeys: string[] = [];

        for (let key of keys) {
            let chunkKey: string = keyChunk(modelSetKey, key);
            if (keysByChunkKey[chunkKey] == null) keysByChunkKey[chunkKey] = [];
            keysByChunkKey[chunkKey].push(key);
            chunkKeys.push(chunkKey);
        }

        let promises = [];
        for (let chunkKey of chunkKeys) {
            let keysForThisChunk = keysByChunkKey[chunkKey];
            promises.push(
                this.getItemKeysForKeys(keysForThisChunk, modelSetKey, chunkKey)
            );
        }

        return Promise.all(promises).then(
            (promiseResults: ItemKeyTuple[][]) => {
                let objects: ItemKeyTuple[] = [];
                for (let results of promiseResults) {
                    for (let result of results) {
                        objects.push(result);
                    }
                }
                return objects;
            }
        );
    }

    /** Get ItemKeyIndexs for Object ID
     *
     * Get the objects with matching keywords from the index..
     *
     */
    private async getItemKeysForKeys(
        keys: string[],
        modelSetKey: string,
        chunkKey: string
    ): Promise<ItemKeyTuple[]> {
        if (!this.index.updateDateByChunkKey.hasOwnProperty(chunkKey)) {
            console.log(`ObjectIDs: ${keys} doesn't appear in the index`);
            return Promise.resolve([]);
        }

        const vortexMsg: string = await this.storage.loadTuplesEncoded(
            new ItemKeyIndexChunkTupleSelector(chunkKey)
        );
        if (vortexMsg == null) {
            return [];
        }

        const payload: Payload = await Payload.fromEncodedPayload(vortexMsg);
        const chunkData: { [key: number]: string } = JSON.parse(
            <any>payload.tuples[0]
        );
        let foundItemKeyIndexs: ItemKeyTuple[] = [];

        for (let key of keys) {
            // Find the keyword, we're just iterating
            if (!chunkData.hasOwnProperty(key)) {
                console.log(
                    `WARNING: ItemKeyIndex ${key} is missing from index,` +
                        ` chunkKey ${chunkKey}`
                );
                continue;
            }

            let packedJson = chunkData[key];
            foundItemKeyIndexs.push(
                new ItemKeyTuple().unpackJson(key, packedJson, modelSetKey)
            );
        }

        return foundItemKeyIndexs;
    }
}
