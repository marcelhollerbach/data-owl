import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

export interface CompileResultItem {
  line_index: number,
  item_index: number,
  title: string,
  message: string,
}

export interface CompileResults {
  happenings: CompileResultItem[]
}


export class SearchItem {
  constructor(public type:string, public value:string) {}
}

export class SearchLine {
  constructor(public intersection_request: SearchItem[]) { }
}

export class SearchRequst {
  constructor(public union_requests: SearchLine[]) {}
}

@Injectable({
  providedIn: 'root'
})
export class SearchService {

  constructor(private client: HttpClient) { }

  public search(req: SearchRequst):Observable<string[]> {
    return this.client.post<string[]>(environment.server + "v1/search/apply", req)
  }

  public compile(req: SearchRequst):Observable<CompileResults> {
    return this.client.post<CompileResults>(environment.server + "v1/search/compile", req)

  }
}
