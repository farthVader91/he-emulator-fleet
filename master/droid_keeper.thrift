struct ConnParams {
  1: string host,
  2: string port,
}

exception ApplicationException {
  1: string msg
}

service DroidKeeper {
   void ping(),

   string get_package_name(1: string apk_url) throws (
          1: ApplicationException ae),

   ConnParams get_endpoint_for_user(1: string user),
}
