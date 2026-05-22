import axios from "axios";
import {useAppStore} from "@/stores/app";

export async function getSpaceByShortName(shortName){
  const store = useAppStore();

  if (shortName.match(/^[0-9A-F]{8}-[0-9A-F]{4}-[4][0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i)) {
    return shortName
  }
  const tmp = await axios.get(`/api/v1/space/by-short/${shortName}`)
  store.openSpaceId = tmp.data.id
  return tmp.data.id
}
