<?php
// Simple PHP reverse proxy to forward requests to your local Ollama via ngrok
// Deployed on shared hosting (cPanel). Adds permissive CORS headers and streams responses.

// 1) Set your upstream URL (your ngrok HTTPS URL without trailing slash)
$UPSTREAM = 'https://d6a807e37f79.ngrok-free.app';

// CORS
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
  http_response_code(204);
  exit;
}

$path = isset($_SERVER['PATH_INFO']) ? $_SERVER['PATH_INFO'] : '';
if ($path === '') {
  // Support when accessed as /ollama without extra path
  $path = str_replace('/ollama', '', parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH));
}
$target = rtrim($UPSTREAM, '/') . $path;

$ch = curl_init($target);
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, false); // stream directly
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);

// Forward body for POST/PUT/PATCH
$input = file_get_contents('php://input');
if ($input !== false && strlen($input) > 0) {
  curl_setopt($ch, CURLOPT_POSTFIELDS, $input);
}

// Forward content-type header
$headers = [];
foreach (getallheaders() as $k => $v) {
  // Skip host to avoid mismatch
  if (strtolower($k) === 'host') continue;
  $headers[] = $k . ': ' . $v;
}
if (!array_filter($headers, fn($h) => stripos($h, 'Content-Type:') === 0)) {
  $headers[] = 'Content-Type: application/json';
}
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

// Stream response headers + body
$responseHeadersSent = false;
curl_setopt($ch, CURLOPT_WRITEFUNCTION, function($ch, $data) use (&$responseHeadersSent) {
  echo $data;
  if (ob_get_level()) { ob_flush(); }
  flush();
  return strlen($data);
});

// Handle headers
curl_setopt($ch, CURLOPT_HEADERFUNCTION, function($ch, $header) use (&$responseHeadersSent) {
  $len = strlen($header);
  if (stripos($header, 'Transfer-Encoding:') === 0) return $len; // let PHP handle
  if (stripos($header, 'Connection:') === 0) return $len;
  if (stripos($header, 'Access-Control-Allow-Origin:') === 0) return $len;
  if (!$responseHeadersSent) {
    // Pass through content-type/status line
    header($header, false);
  }
  return $len;
});

$ok = curl_exec($ch);
if ($ok === false) {
  http_response_code(502);
  header('Content-Type: application/json');
  echo json_encode(['error' => 'Proxy request failed', 'detail' => curl_error($ch)]);
}
curl_close($ch);

