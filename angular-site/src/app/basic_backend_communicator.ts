import { HttpErrorResponse } from '@angular/common/http';
import { MatDialogRef } from '@angular/material/dialog';
import { Observer } from 'rxjs';

export class BackendInteractionHandler<T,U> implements Observer<T> {
    next: (value: T) => void;
    error: (err: HttpErrorResponse) => void;
    complete: () => void;

    constructor(public backend: BackendCommunicator<U>) {
        this.next = (_) => {
            backend.in_flight = false;
            backend.dialogRef.close();
        };
        this.error = (err) => {
            backend.in_flight = false;
            backend.error.backend = err.error;
            backend.error.display = true;
            console.log(err)
        };
        this.complete = () => {
        };
    }
}

export interface BackendCommunicator<T> {
    dialogRef: MatDialogRef<T>;
    error: BackendError;
    in_flight: boolean;
}

export interface BackendResponse {
    error: string;
    message: string;
}

export class BackendError {
    static default(): BackendError {
        return new BackendError(false, {
            "error" : "",
            "message" : ""
        })
    }
    constructor(public display: boolean, public backend: BackendResponse) { }
}