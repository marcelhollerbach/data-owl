import { Component } from '@angular/core';
import { MatChipInputEvent, MatChipEditedEvent } from '@angular/material/chips';
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { SearchItem, SearchLine, SearchRequst, SearchService } from '../search.service';
import { AbstractControl, AsyncValidatorFn, FormControl, FormGroupDirective, NgForm, ValidationErrors } from '@angular/forms';
import { Observable, map } from 'rxjs';

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
  selector: 'app-wizard',
  templateUrl: './wizard.component.html',
  styleUrls: ['./wizard.component.scss']
})
export class WizardComponent {
  chip_control = new FormControl<UiSearchTerm[]>([]);
  errorStateMatcher = new ErrorStateMatcher();
  addOnBlur = true;
  readonly separatorKeysCodes = [ENTER, COMMA] as const;
  search_results: string[];
  terms = [new UiSearchTerm("type:test"), new UiSearchTerm("contains:something"), new UiSearchTerm("test")]

  constructor(private service: SearchService) {
    this.search_results = []
    this.chip_control.addAsyncValidators(this.childValidator())
  }

  add(event: MatChipInputEvent): void {
    const value = (event.value || '').trim();

    if (value) {
      this.terms.push(new UiSearchTerm(value));
    }

    event.chipInput!.clear();
  }

  remove(fruit: UiSearchTerm): void {
    const index = this.terms.indexOf(fruit);

    if (index >= 0) {
      this.terms.splice(index, 1);
    }
  }

  edit(fruit: UiSearchTerm, event: MatChipEditedEvent) {
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

  toSearchRequest() {
    return new SearchRequst([new SearchLine(this.terms.map((m) => m.toSearchItem()))])
  }

  search() {
    this.service.search(this.toSearchRequest()).subscribe(
      (m) => {
        this.search_results = m
      }
    )
  }
  childValidator(): AsyncValidatorFn {
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
