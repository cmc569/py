<?php
require_once 'pdodb.php';

$conn = new foreclosureDB;

$sql = 'SELECT * FROM `case_map` WHERE cAddress LIKE "新北市%" AND cAddress NOT LIKE "%地號%" AND cMapLabel = 4 AND cPath = "" ORDER BY id DESC LIMIT 1000;';
$rs = $conn->all($sql);

if (count($rs) > 0) {
    foreach ($rs as $v) {
        $addr = $v['cAddress'];
        echo 'id = '.$v['id'].', address = '.$v['cAddress']." ... ";
        
        $url = 'http://twhggeo.azurewebsites.net/api/?address='.urlencode($addr).'&format=json';
        $json = file_get_contents($url);
        $arr = json_decode($json, true);
        
        if (!empty($arr['WGS84_Y']) && !empty($arr['WGS84_X'])) {
            $sql = 'UPDATE `case_map` SET `cLat` = :lat, `cLng` = :lng WHERE `id` = :id;';
            $res = $conn->exeSql($sql, ['lat' => $arr['WGS84_Y'], 'lng' => $arr['WGS84_X'], 'id' => $v['id']]);

            if ($res) echo "OK\n";
            else echo "NG\n";
        }
        
        unset($addr, $url, $json, $arr, $sql, $res);
    }
}
?>