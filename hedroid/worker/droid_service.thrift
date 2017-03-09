struct ConnParams {
  1: string host,
  2: string port,
  3: optional string password,
}

exception ApplicationException {
  1: string msg
}

service DroidService {
   void ping(),

   string get_package_name(1: string apk_url) throws (
          1: ApplicationException ae),

   ConnParams get_endpoint(1: string endpoint_id),

   bool run_operation(1: string endpoint_id, 2: string operation, 3: string apk_url) throws (
          1: ApplicationException ae),
}
