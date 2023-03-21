import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export class DataEntryInstance {
  constructor(public title: string, public trait_instances: any) { }
}

export class DataEntry {
  constructor(public id: string, public instances: DataEntryInstance[]) { }
};

export interface DataEntryExploration {
  id: string,
  Description: string,
  Name: string
}

export interface DataEntryPostReply {
  id: string
  name: string
  description: string
}


@Injectable({
  providedIn: 'root'
})
export class DataEntriesService {
  constructor(private client: HttpClient) { }
  public findAll(): Observable<DataEntryExploration[]> {
    return this.client.get<DataEntryExploration[]>(environment.server + "v1/dataEntries")
  }
  public put(entry: DataEntry): Observable<DataEntryPostReply> {
    return this.client.put<DataEntryPostReply>(environment.server + "v1/dataEntry", entry)
  }
  public post(entry: DataEntry): Observable<DataEntryPostReply> {
    return this.client.post<DataEntryPostReply>(environment.server + "v1/dataEntry/" + entry.id, entry)
  }
  public find(id: string): Observable<DataEntry> {
    return this.client.get<DataEntry>(environment.server + "v1/dataEntry/" + id)
  }
  public delete(id: string) {
    return this.client.delete(environment.server + "v1/dataEntry/" + id)
  }
}
