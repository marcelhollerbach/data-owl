import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, race, ReplaySubject, tap } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface DataClassField {
  name: string,
  description: string,
  format: string
}

export interface DataClass {
   title : string,
   version: string
   description: string,
   fields: DataClassField[]
}

@Injectable({
  providedIn: 'root'
})
export class DataTraitService {

  constructor(private client: HttpClient) {
  }

  public findAll():Observable<DataClass[]> {
    return this.client.get<DataClass[]>(environment.server + "v1/dataTrait/")
  }

}
