import { Component, Inject, ViewChild } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { EMPTY, exhaustMap, map, Observable, shareReplay, zip } from 'rxjs';
import { DataClass, DataClassField, DataTraitService } from '../../data-trait.service';
import { DataEntriesService, DataEntry, DataEntryInstance } from '../../data-entries.service';
import { NgForm } from '@angular/forms';
import { fetchValues } from './util'
import { MatExpansionPanel } from '@angular/material/expansion';
import { MatChipListbox } from '@angular/material/chips';
import { BackendCommunicator, BackendError, BackendInteractionHandler } from 'src/app/basic_backend_communicator';
import { HttpErrorResponse } from '@angular/common/http';



class UITraitDataLine {
  constructor(public instance: string, public meta: DataClassField) { }
  validate() {
  }
}

class UiTrait {
  constructor(public klass: DataClass, public instances: UITraitDataLine[]) { }

  to_backend_instance(): DataEntryInstance{
    let result_instance = new Map<string, string>();

    for (let instance of this.instances) {
      instance.validate()
      result_instance.set(instance.meta.name, instance.instance);
    }
    return new DataEntryInstance(this.klass.title, Object.fromEntries(result_instance))
  }
}

function makeUiStructure(dclass: DataClass, instance?: DataEntryInstance): UiTrait {
  let result: UITraitDataLine[] = []
  for (let field of dclass.fields) {
    result.push(new UITraitDataLine(typeof instance !== 'undefined' ? instance.trait_instances[field.name] : '', field))
  }

  return new UiTrait(dclass, result)
}

@Component({
  selector: 'new-data-entry',
  templateUrl: 'new-data-entry.html',
})
export class NewDataEntry implements BackendCommunicator<NewDataEntry>{
  data_traits$: Observable<DataClass[]>;
  data_instance: UiTrait[];

  implemented_traits: string[];
  error: BackendError;
  dialogRef: MatDialogRef<NewDataEntry>;
  in_flight: boolean;

  constructor(@Inject(MAT_DIALOG_DATA) public data: { id: string }, dialogRef: MatDialogRef<NewDataEntry>, private data_entry_service: DataEntriesService, private data_trait_service: DataTraitService) {
    this.data_traits$ = this.data_trait_service.findAll();
    let data_entry$ = data.id != "" ? this.data_entry_service.find(data.id) : EMPTY;
    this.data_instance = []

    this.implemented_traits = ['Default']
    this.in_flight = true;
    this.dialogRef = dialogRef;
    this.error = BackendError.default();

    if (data.id != "") {
      data_entry$.subscribe((m) => {
        this.implemented_traits = m.instances.map((m) => m.title)
      })
      zip(this.data_traits$, data_entry$).pipe(
        map(v => {
          let dclass = v[0]
          let instance = v[1]
          return dclass.map((klass) => {
            let res = instance.instances.find((elem) => elem.title == klass.title)
            return makeUiStructure(klass, res);
          })
        })
      ).subscribe((m) => {this.in_flight = false; this.data_instance = m });
    } else {
      this.data_traits$.pipe(
        map(v => v.map((klass) => makeUiStructure(klass, undefined)))
      ).subscribe((m) => {this.in_flight = false; this.data_instance = m });
    }
  }

  assigned_traits_changed(source: MatChipListbox) {
    this.implemented_traits = source.value
  }

  deleteEntry() {
    this.in_flight = true;
    this.data_entry_service.delete(this.data.id).subscribe(new BackendInteractionHandler(this))
  }

  updateEntry() {
    //assertion each element in data_instance is set for all data_trait
    let entry = new DataEntry(this.data.id, this.data_instance
      .filter((m) => this.implemented_traits.indexOf(m.klass.title) != -1)
      .map((m) => m.to_backend_instance()))
    this.in_flight = true
    if (this.data.id != '') {
      this.data_entry_service.post(entry).subscribe(new BackendInteractionHandler(this))
    } else {
      this.data_entry_service.put(entry).subscribe(new BackendInteractionHandler(this))
    }
  }
}