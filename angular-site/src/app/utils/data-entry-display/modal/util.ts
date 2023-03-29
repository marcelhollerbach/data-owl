import { DataClass } from "src/app/data-trait.service";
import { DataEntryInstance, DataEntry } from "src/app/data-entries.service";

function getDataEntryFromFormValue(trait_for_search: DataClass, value: any) : DataEntryInstance {
    var fields = trait_for_search.fields;
    let result_instance = new Map<string, string>();

    fields.forEach(element => {
      let name = trait_for_search.title + "-" + element.name;
      let user_input = value[name];
      //FIXME validate user_input
      result_instance.set(element.name, user_input);
    });
    //FIXME validate that all values are set
    return new DataEntryInstance(
      trait_for_search.title,
      Object.fromEntries(result_instance)
    );
    
}
export function fetchValues(dataClasses: DataClass[], values: any, id: string): DataEntry {
    return new DataEntry(id, dataClasses.map((m) => getDataEntryFromFormValue(m, values)));

}