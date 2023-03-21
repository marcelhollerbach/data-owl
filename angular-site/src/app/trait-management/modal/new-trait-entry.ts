import { Component, Inject, ViewChild } from '@angular/core';
import { NgForm } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DataClassField, DataTrait, DataTraitManagementService } from 'src/app/data-trait-management.service';
import { BackendCommunicator, BackendError, BackendInteractionHandler } from '../../basic_backend_communicator';

class Field {
    constructor(public data: DataClassField, public open: boolean, public id: number) { }
}

@Component({
    selector: 'new-trait-entry',
    templateUrl: 'new-trait-entry.html',
})
export class NewTraitEntry implements BackendCommunicator<NewTraitEntry> {

    @ViewChild('f', { static: true }) value?: NgForm;
    error: BackendError;
    dialogRef: MatDialogRef<NewTraitEntry>;
    in_flight: boolean;

    fields: Field[];
    title: string;
    description: string;
    version: number;

    constructor(@Inject(MAT_DIALOG_DATA) public data: { id: string }, dialogRef: MatDialogRef<NewTraitEntry>, private trait_mgt_service: DataTraitManagementService) {
        this.in_flight = false
        this.fields = []
        this.title = ""
        this.description = ""
        this.version = 0;
        this.error = BackendError.default();
        this.dialogRef = dialogRef
        if (data.id != undefined) {
            this.in_flight = true
            trait_mgt_service.find(data.id).subscribe((v) => {
                this.title = v.title
                this.version = v.version
                this.description = v.description
                this.fields = v.fields.map((m, index) => new Field(m, false, index))
                this.in_flight = false
            })
        }
    }

    addDummyField() {
        this.fields.push(new Field(new DataClassField("Change-me", "", "simple_string"), true, Math.max(...this.fields.map((x) => x.id)) + 1))
    }

    deleteEntry() {
        this.in_flight = true
        this.trait_mgt_service.delete(this.title).subscribe(new BackendInteractionHandler(this))
    }
    updateEntry() {
        this.in_flight = true
        if (this.data.id != undefined) {
            this.trait_mgt_service.post(this.data.id, new DataTrait(this.title, this.description, this.fields.map((m) => m.data))).subscribe(new BackendInteractionHandler(this));
        } else {
            this.trait_mgt_service.put(new DataTrait(this.title, this.description, this.fields.map((m) => m.data))).subscribe(new BackendInteractionHandler(this));
        }
        
    }
}

