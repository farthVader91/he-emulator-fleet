struct ConnParams {
  1: string host,
  2: string port,
}

service MasterService {
   void ping(),

   string get_package_name(1: string apk_url),

   ConnParams get_endpoint(1: string user),

   bool install_apk(1: string endpoint_id, 2: string apk_url),

   bool start_package(1: string endpoint_id, 2: string package_name),
}
