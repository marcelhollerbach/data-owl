import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
import { DataClass } from './data-trait.service';

export class DataClassField {
  constructor(public name: string, public description: string, public format: string) { }
}

export class DataTrait {
  public version: number;
  constructor(public title: string, public description: string, public fields: DataClassField[]) {
    this.version = 0
  }
}

export interface DataTraitClass {
  title: string,
  description: string,
  immutable: boolean
  versions: DataClass[]
}

export interface DataTraitPostReply {
  id: string
}

@Injectable({
  providedIn: 'root'
})
export class DataTraitManagementService {
  constructor(private client: HttpClient) { }

  public findAll(): Observable<DataTraitClass[]> {
    return this.client.get<DataTraitClass[]>(environment.server + "v1/dataTraitManagement/")
  }
  public put(entry: DataTrait): Observable<DataTraitPostReply> {
    return this.client.put<DataTraitPostReply>(environment.server + "v1/dataTraitManagement/", entry)
  }
  public post(id: string, entry: DataTrait): Observable<DataTraitPostReply> {
    return this.client.post<DataTraitPostReply>(environment.server + "v1/dataTraitManagement/" + id, entry)
  }
  public find(id: string): Observable<DataTrait> {
    return this.client.get<DataTrait>(environment.server + "v1/dataTraitManagement/" + id)
  }
  public delete(id: string): Observable<any> {
    return this.client.delete(environment.server + "v1/dataTraitManagement/" + id)
  }
}
