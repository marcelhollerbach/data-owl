import { DataSource } from '@angular/cdk/collections';
import { ENTER, COMMA } from '@angular/cdk/keycodes';
import { Component } from '@angular/core';
import { AbstractControl, AsyncValidatorFn, FormControl, FormGroupDirective, NgForm, ValidationErrors } from '@angular/forms';
import { MatChipInputEvent, MatChipEditedEvent } from '@angular/material/chips';
import { Observable, map } from 'rxjs';
import { SearchItem, SearchResult, SearchService, SearchRequst, SearchLine } from 'src/app/search.service';
import { EmptyDataSource } from '../EmptyDataSource';

class UiSearchTerm {

  type: string;
  value: string;
  error: boolean;

  title: string;
  message: string;

  constructor(name: string) {
    this.error = false;
    this.title = "";
    this.message = "";
    let split = name.split(":")
    if (split.length == 2) {
      this.type = split[0]
      this.value = split[1]
    } else if (split.length == 1) {
      this.type = "contains"
      this.value = split[0]
    } else {
      this.type = ''
      this.value = name
    }
  }
  syntax() {
    return this.type + ":" + this.value
  }
  toSearchItem() {
    return new SearchItem(this.type, this.value)
  }

  mark_error(title: string, message: string) {
    this.error = true;
    this.title = title;
    this.message = message
  }
  reset_error() {
    this.error = false;
  }
}

export class ErrorStateMatcher implements ErrorStateMatcher {
  isErrorState(control: FormControl | null, form: FormGroupDirective | NgForm | null): boolean {
    return !!(control && (control.invalid && !control.pending));
  }
}

@Component({
  selector: 'app-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.scss']
})
export class SearchBarComponent {
  chip_control = new FormControl<UiSearchTerm[]>([]);
  errorStateMatcher = new ErrorStateMatcher();
  addOnBlur = true;
  readonly separatorKeysCodes = [ENTER, COMMA] as const;
  displayedColumns= ["Name", "Description"]
  terms = [new UiSearchTerm("type:Default")]
  dataSource: DataSource<SearchResult> = new EmptyDataSource<SearchResult>;

  constructor(private service: SearchService) {
    this.chip_control.addAsyncValidators(this.childValidator())
  }

  protected add(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();

    if (value) {
      this.terms.push(new UiSearchTerm(value));
    }

    event.chipInput!.clear();
  }

  protected remove(fruit: UiSearchTerm): void {
    const index = this.terms.indexOf(fruit);

    if (index >= 0) {
      this.terms.splice(index, 1);
    }
  }

  protected edit(fruit: UiSearchTerm, event: MatChipEditedEvent) {
    const value = event.value.trim();

    if (!value) {
      this.remove(fruit);
      return;
    }

    const index = this.terms.indexOf(fruit);
    if (index >= 0) {
      this.terms[index] = new UiSearchTerm(value);
    }
  }

  public toSearchRequest() {
    return new SearchRequst([new SearchLine(this.terms.map((m) => m.toSearchItem()))])
  }

  private childValidator(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      console.log(control.value)
      let compiler = this.service.compile(this.toSearchRequest())
      compiler.subscribe(
        (m) => {
          if (m.happenings.length != 0) {
            for (let error of m.happenings) {
              let item = this.terms[error.item_index]
              item.error = true;
              item.mark_error(error.title, error.message)
            }
          } else {
            for (let term of this.terms) {
              term.reset_error();
            }
          }
        }
      )
      return compiler.pipe(
        map(m => {
          let errors = m.happenings.map(m => m.title)
          if (errors.length == 0) {
            return null;
          } else {
            return {"error": errors.join("; ")};
          }
        }
        )
      )
    };
  }
}
