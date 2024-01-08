/**
 * Copyright 2022 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

# CDN load balancer with Cloud bucket as backend

# [START cloudloadbalancing_external_cdn_lb_with_backend_bucket_parent_tag]
# [START cloudloadbalancing_cdn_with_backend_bucket_cloud_storage_bucket]
# Cloud Storage bucket
resource "random_id" "bucket_prefix" {
  byte_length = 8
}

resource "google_storage_bucket" "default" {
    project = "ml-demo-384110"

  name                        = "${random_id.bucket_prefix.hex}-my-bucket"
  location                    = "europe-west1"
  uniform_bucket_level_access = true
  storage_class               = "STANDARD"
  // delete bucket and contents on destroy.
  force_destroy = true
  // Assign specialty files
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
}

# [END cloudloadbalancing_cdn_with_backend_bucket_cloud_storage_bucket]

# [START cloudloadbalancing_cdn_with_backend_bucket_make_public]
# make bucket public
resource "google_storage_bucket_iam_member" "default" {
  bucket = google_storage_bucket.default.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"    
  

}
# [END cloudloadbalancing_cdn_with_backend_bucket_make_public]

# [START cloudloadbalancing_cdn_with_backend_bucket_index_page]
resource "google_storage_bucket_object" "index_page" {
  name    = "index-http.html"
  bucket  = google_storage_bucket.default.name
  content = <<-EOT
    
    

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Video Player</title>
</head>
<body>
    <h1>Congratulations on setting up Google Cloud CDN with Storage backend!</h1>

    <video id="player"  autoplay loop muted>
        <source src="http://${google_compute_global_forwarding_rule.default.ip_address}/${google_storage_bucket_object.test_video.name}" type="video/mp4">
        <p>Your browser does not support HTML5 video.</p>
    </video>


    <script>
        // Optional: Play the video automatically
        const player = document.getElementById("player");
    </script>
</body>
</html>

  EOT
}

resource "google_storage_bucket_object" "index_page_https" {
  name    = "index.html"
  bucket  = google_storage_bucket.default.name
  content = <<-EOT
    
    

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Video Player</title>
</head>
<body>
    <h1>Congratulations on setting up Google Cloud CDN with Storage backend!</h1>

    <video id="player"  autoplay loop muted>
        <source src="https://${google_compute_global_forwarding_rule.default.ip_address}/${google_storage_bucket_object.test_video.name}" type="video/mp4">
        <p>Your browser does not support HTML5 video.</p>
    </video>


    <script>
        // Optional: Play the video automatically
        const player = document.getElementById("player");
    </script>
</body>
</html>

  EOT
}


resource "google_storage_bucket_object" "index_nocdn_page" {
  name    = "index-nocdn.html"
  bucket  = google_storage_bucket.default.name
  content = <<-EOT
    
    

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Video Player</title>
</head>
<body>
    <h1>Congratulations on setting up backend cloud storage backend!</h1>

    <video id="player"  autoplay loop muted>
        <source src=https://storage.googleapis.com/${google_storage_bucket.default.name}/${google_storage_bucket_object.test_video.name}" type="video/mp4">
        <p>Your browser does not support HTML5 video.</p>
    </video>


    <script>
        // Optional: Play the video automatically
        const player = document.getElementById("player");
    </script>
</body>
</html>

  EOT
}
# [END cloudloadbalancing_cdn_with_backend_bucket_index_page]

# [START cloudloadbalancing_cdn_with_backend_bucket_error_page]
resource "google_storage_bucket_object" "error_page" {
  name    = "404-page"
  bucket  = google_storage_bucket.default.name
  content = <<-EOT
    <html><body>
    <h1>404 Error: Object you are looking for is no longer available!</h1>
    </body></html>
  EOT
}
# [END cloudloadbalancing_cdn_with_backend_bucket_error_page]

# [START cloudloadbalancing_cdn_with_backend_bucket_image]
# image object for testing, try to access http://<your_lb_ip_address>/test.jpg
resource "google_storage_bucket_object" "test_video" {
  name = "001510514.mp4"
  # Uncomment and add valid path to an object.
  #  source       = "/path/to/an/object"
  #  content_type = "image/jpeg"

  # Delete after uncommenting above source and content_type attributes
  source      = "./video/001510514.mp4"
  content_type = "video/mp4"
  bucket = google_storage_bucket.default.name
}
# [END cloudloadbalancing_cdn_with_backend_bucket_image]

# [START cloudloadbalancing_cdn_with_backend_bucket_ip_address]
# reserve IP address
resource "google_compute_global_address" "default" {
  name = "frontend-ip"
      project = "ml-demo-384110"

}
# [END cloudloadbalancing_cdn_with_backend_bucket_ip_address]

# [START cloudloadbalancing_cdn_with_backend_bucket_forwarding_rule]
# forwarding rule
resource "google_compute_global_forwarding_rule" "default" {
    project = "ml-demo-384110"

  name                  = "http-lb-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "80"
  target                = google_compute_target_http_proxy.default.id
  ip_address            = google_compute_global_address.default.id
}

resource "google_compute_global_forwarding_rule" "default-https" {
    project = "ml-demo-384110"

  name                  = "http-lb-forwarding-rule-https"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "443"
  
  target                = google_compute_target_https_proxy.default.id
  ip_address            = google_compute_global_address.default.id
}

# [END cloudloadbalancing_cdn_with_backend_bucket_forwarding_rule]

# [START cloudloadbalancing_cdn_with_backend_bucket_http_proxy]
# http proxy
resource "google_compute_target_http_proxy" "default" {
  name    = "http-lb-proxy"
  url_map = google_compute_url_map.default-http.id
    project = "ml-demo-384110"

}
# [END cloudloadbalancing_cdn_with_backend_bucket_http_proxy]

# https proxy
resource "google_compute_target_https_proxy" "default" {
  name    = "https-lb-proxy"
  url_map = google_compute_url_map.default-http.id
    project = "ml-demo-384110"
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]

}


# [START cloudloadbalancing_cdn_with_backend_bucket_url_map]
# url map
resource "google_compute_url_map" "default-http" {
  project = "ml-demo-384110"

  name            = "http-lb"
  default_service = google_compute_backend_bucket.default.id
}
# [END cloudloadbalancing_cdn_with_backend_bucket_url_map]

# [START cloudloadbalancing_cdn_with_backend_bucket_backend_bucket]
# backend bucket with CDN policy with default ttl settings
resource "google_compute_backend_bucket" "default" {
    project = "ml-demo-384110"

  name        = "media-backend-bucket"
  description = "Contains beautiful video"
  bucket_name = google_storage_bucket.default.name
  enable_cdn  = true
  cdn_policy {
    cache_mode        = "CACHE_ALL_STATIC"
    client_ttl        = 3600
    default_ttl       = 3600
    max_ttl           = 86400
    negative_caching  = true
    serve_while_stale = 86400
  }
}
# [END cloudloadbalancing_cdn_with_backend_bucket_backend_bucket]
# [END cloudloadbalancing_external_cdn_lb_with_backend_bucket_parent_tag]


resource "google_compute_managed_ssl_certificate" "default" {
      project = "ml-demo-384110"

  name = "cert"

  managed {
    domains = ["cdn.lab-demo.cloud."]
  }
}

 
# [START cloudloadbalancing_target_https_proxy_basic]
resource "google_compute_target_https_proxy" "default2" {
      project = "ml-demo-384110"

  name             = "test-proxy2"
  url_map = google_compute_url_map.default-http.id
#  ssl_certificates = [google_compute_ssl_certificate.default.id]
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]

}

resource "tls_private_key" "example" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "example" {
  private_key_pem = tls_private_key.example.private_key_pem

  # Certificate expires after 12 hours.
  validity_period_hours = 12

  # Generate a new certificate if Terraform is run within three
  # hours of the certificate's expiration time.
  early_renewal_hours = 3

  # Reasonable set of uses for a server SSL certificate.
  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]

  dns_names = ["cdn.lab-demo.cloud"]

  subject {
    common_name  = "lab-demo.cloud"
    organization = "Julien demo Examples, Inc"
  }
}

resource "google_compute_ssl_certificate" "default" {
      project = "ml-demo-384110"

  name        = "my-certificate"
  private_key = tls_private_key.example.private_key_pem
  certificate = tls_self_signed_cert.example.cert_pem
}

resource "google_compute_url_map" "default" {
      project = "ml-demo-384110"

  name        = "url-map"
  description = "a description"

  default_service = google_compute_backend_service.default.id

  host_rule {
    hosts        = ["cdn.lab-demo.cloud"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.default.id


  }
}

resource "google_compute_backend_service" "default" {
      project = "ml-demo-384110"

  name        = "backend-service"
  port_name   = "http"
  protocol    = "HTTP"
  timeout_sec = 10

  health_checks = [google_compute_http_health_check.default.id]
}

resource "google_compute_http_health_check" "default" {
    project = "ml-demo-384110"

  name               = "http-health-check"
  request_path       = "/"
  check_interval_sec = 1
  timeout_sec        = 1
}
# [END cloudloadbalancing_target_https_proxy_basic]



resource "google_dns_record_set"  "cdn_record" {
    project = "ml-demo-384110"
    managed_zone = "lab-demo-cloud"
  
  
  name = "cdn.lab-demo.cloud."
  type = "A"
  ttl = 300

  rrdatas = [
   google_compute_global_forwarding_rule.default.ip_address
  ]
}



# output ip in terraform      

output "cdn_ip_address" {
  value = google_compute_global_forwarding_rule.default.ip_address
  description = "IP address of the CDN"  
}
output "name" {
  value = google_storage_bucket_object.test_video.name
  description = "name of the video"  
}
output "media_link" {
  value = google_storage_bucket_object.test_video.output_name
  description = "media link of the video"  
}