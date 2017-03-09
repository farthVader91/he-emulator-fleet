struct DroidRequest {
  1: string user,
  2: optional string apk_url,
  3: optional string op,
}

struct ConnParams {
  1: string host,
  2: string port,
  3: optional string password,
}

exception ApplicationException {
  1: string msg
}

service DroidKeeper {
   void ping(),

   string get_package_name(1: string apk_url) throws (
          1: ApplicationException ae),

   ConnParams get_endpoint_for_user(1: string user) throws (
          1: ApplicationException ae),

   bool interact_with_endpoint(1: DroidRequest dr) throws (
          1: ApplicationException ae),

   oneway void release_endpoint_for_user(1: string user),
}
