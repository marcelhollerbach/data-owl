import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { EMPTY, filter, map, max, Observable, zip } from 'rxjs';
import { DataEntriesService, DataEntry, DataEntryInstance } from '../../../data-entries.service';
import { MatChipListbox } from '@angular/material/chips';
import { BackendCommunicator, BackendError, BackendInteractionHandler } from 'src/app/basic_backend_communicator';
import { DataClass, DataClassField, DataTraitClass, DataTraitManagementService } from 'src/app/data-trait-management.service';

enum DataTraitUIBucket{
  DEFAULTS = 10,
  READONLY = 2,
  REST = 0
}

class UITraitDataLine {
  constructor(public instance: string, public meta: DataClassField, public readOnly:boolean) { }
  validate() {
  }
}

class UiTrait {
  constructor(public klass: DataTraitClass, public version: DataClass, public version_upgrade_available:boolean, public instances: UITraitDataLine[]) { }

  get_ui_bucket() : DataTraitUIBucket {
    if (this.klass.enabled_per_default)
      return DataTraitUIBucket.DEFAULTS;
    else if (this.klass.readonly)
      return DataTraitUIBucket.READONLY;
    else
      return DataTraitUIBucket.REST
  }

  to_backend_instance(): DataEntryInstance{
    let result_instance = new Map<string, string>();

    for (let instance of this.instances) {
      instance.validate()
      result_instance.set(instance.meta.name, instance.instance);
    }
    return new DataEntryInstance(this.klass.title, '0', Object.fromEntries(result_instance))
  }
  static from_raw(raw: DataTraitClass, instance?: DataEntryInstance) {
    let result: UITraitDataLine[] = []

    let version = raw.versions[0] //FIXME is this here always the highest ?
    let upgrade_available = false
    if (typeof instance !== 'undefined') {
      let defined_version = raw.versions.find((elem) => elem.version == instance?.version) as DataClass
      if (defined_version != version) {
        upgrade_available = true
        version = defined_version
      }
    }
  
    for (let field of version?.fields) {
      let instance_value = ''
      if (typeof instance !== 'undefined') {
        instance_value = instance.trait_instances[field.name]
      } 
      result.push(new UITraitDataLine(instance_value, field, raw.readonly))
    }
  
    return new UiTrait(raw, version, upgrade_available, result)    
  }
}

@Component({
  selector: 'new-data-entry',
  templateUrl: 'new-data-entry.html',
})
export class NewDataEntry implements BackendCommunicator<NewDataEntry>{

  available_traits$: Observable<DataTraitClass[]>;
  data_instance: UiTrait[];

  implemented_traits: string[];
  error: BackendError;
  dialogRef: MatDialogRef<NewDataEntry>;
  in_flight: boolean;

  constructor(@Inject(MAT_DIALOG_DATA) public data: { id: string }, dialogRef: MatDialogRef<NewDataEntry>, private data_entry_service: DataEntriesService, private data_trait_service: DataTraitManagementService) {
    this.data_instance = []
    this.implemented_traits = []
    this.dialogRef = dialogRef;
    this.error = BackendError.default();

    this.in_flight = true;
    let raw_data_traits$ = this.data_trait_service.findAll();
    this.available_traits$ = raw_data_traits$.pipe(
      map(v => v.filter(m => !m.readonly))
    )

    if (this.isUpdate()) {
      /**
       * When Updating, we display readonly data, but do not enable it in the chip-box
       */ 
      let data_entry$ = this.data_entry_service.find(data.id)
      data_entry$.subscribe((m) => {
        this.implemented_traits = m.instances.map((m) => m.title)
      })
      zip(raw_data_traits$, data_entry$).pipe(
        map(v => {
          let dclass = v[0]
          let instance = v[1]
          return dclass.map((klass) => {
            let res = instance.instances.find((elem) => elem.title == klass.title)
            return UiTrait.from_raw(klass, res);
          })
        })
      ).subscribe((m) => {
        this.in_flight = false; 
        this.data_instance = m.sort((a, b) => {
          let a_klass = a.get_ui_bucket();
          let b_klass = b.get_ui_bucket();
          if (a_klass == b_klass) {
            return (a.klass.title < b.klass.title ? -1 : 1)
          } else {
            return a_klass > b_klass ? -1 : 1
          }
        })
      });
    } else {
      /**
       * When Creating, we hide everything which is readonly, as its not existing yet
       */ 
      raw_data_traits$.subscribe(m => {
        let implemented_traits = m.filter(m =>  m.enabled_per_default == true).map(m => m.title)
        this.implemented_traits = implemented_traits
      })
      this.available_traits$.pipe(
        map(v => v.map((klass) => UiTrait.from_raw(klass, undefined)))
      ).subscribe((m) => {
        this.data_instance = m 
        this.in_flight = false; 
      });
    }
  }

  protected isUpdate() {
    return this.data.id != "";
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
    entry.instances.find((m) => {
      m.title == ''
    })

    this.removeMetaData(entry, ['Meta-Data']); //FIXME this should be better

    if (this.data.id != '') {
      this.data_entry_service.post(entry).subscribe(new BackendInteractionHandler(this))
    } else {
      this.data_entry_service.put(entry).subscribe(new BackendInteractionHandler(this))
    }
  }

  private removeMetaData(entry: DataEntry, blacklist : string[]) {
    entry.instances = entry.instances.filter(m => blacklist.indexOf(m.title) == -1)
  }

  upgrade_version(target: UiTrait) {
    let goal_version = target.klass.versions[0]
    let current_version = target.version
    let staying_set : string[] = []
    for (let goal_field of goal_version.fields) {
      for (let current_field of current_version.fields) {
        if (goal_field.name == current_field.name && 
            goal_field.description == current_field.description && 
            goal_field.format == goal_field.format) {
              staying_set.push(goal_field.name)
        }
      }
    }
    //filter all staying instances
    target.instances = target.instances.filter((m) => staying_set.indexOf(m.meta.name) != -1)
    let instance = target.to_backend_instance()
    instance.version = goal_version.version
    let new_target = UiTrait.from_raw(target.klass, instance)

    //copy over upgrade
    target.instances = new_target.instances
    target.klass = new_target.klass
    target.version = new_target.version
    target.version_upgrade_available = false;


  }
}