<?php
// Single-file PHP proxy for shared hosting without Rewrite rules
// Usage: /ollama.php?path=/api/tags or /api/chat, streams responses

$UPSTREAM = 'https://d6a807e37f79.ngrok-free.app';

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

$path = isset($_GET['path']) ? $_GET['path'] : '';
if ($path === '' || $path[0] !== '/') { $path = '/' . ltrim($path, '/'); }
$target = rtrim($UPSTREAM, '/') . $path;

$ch = curl_init($target);
// Force HTTP/1.1 for compatibility with some upstreams
if (defined('CURL_HTTP_VERSION_1_1')) {
  curl_setopt($ch, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);
}
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $_SERVER['REQUEST_METHOD']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, false);
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);

$input = file_get_contents('php://input');
if ($input !== false && strlen($input) > 0) {
  curl_setopt($ch, CURLOPT_POSTFIELDS, $input);
}

$headers = [];
foreach (getallheaders() as $k => $v) {
  if (strtolower($k) === 'host') continue;
  $headers[] = $k . ': ' . $v;
}
if (!array_filter($headers, fn($h) => stripos($h, 'Content-Type:') === 0)) {
  $headers[] = 'Content-Type: application/json';
}
// Prefer JSON responses
if (!array_filter($headers, fn($h) => stripos($h, 'Accept:') === 0)) {
  $headers[] = 'Accept: application/json, text/event-stream;q=0.9, */*;q=0.8';
}
// Bypass ngrok browser warning page
$headers[] = 'ngrok-skip-browser-warning: 1';
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

curl_setopt($ch, CURLOPT_WRITEFUNCTION, function($ch, $data) {
  echo $data;
  if (ob_get_level()) { ob_flush(); }
  flush();
  return strlen($data);
});

curl_setopt($ch, CURLOPT_HEADERFUNCTION, function($ch, $header) {
  $len = strlen($header);
  if (stripos($header, 'Transfer-Encoding:') === 0) return $len;
  if (stripos($header, 'Connection:') === 0) return $len;
  if (stripos($header, 'Access-Control-Allow-Origin:') === 0) return $len;
  header($header, false);
  return $len;
});

$ok = curl_exec($ch);
if ($ok === false) {
  http_response_code(502);
  header('Content-Type: application/json');
  echo json_encode(['error' => 'Proxy request failed', 'detail' => curl_error($ch)]);
}
curl_close($ch);
