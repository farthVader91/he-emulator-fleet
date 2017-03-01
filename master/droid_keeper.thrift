struct ConnParams {
  1: string host,
  2: string port,
}

service DroidKeeper {
   void ping(),

   string get_package_name(1: string apk_url),

   ConnParams get_endpoint(1: string user),
}
