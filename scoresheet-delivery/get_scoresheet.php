<?php

$salt = "YOUR-CUSTOM-SALT-DIFFERENT-FOR-EACH-YEAR-OF-THE-COMPETITION";
$prefix = "My-Homebrew-Competition-Name-2018-Scoresheet-";
$scoresheet_path = "/path/to/scoresheets/";

if (isset($_GET['id']) and isset($_GET['hash']) and hash("sha256", $_GET['id'].$salt) == $_GET['hash']) {
  $scoresheetfilename = $scoresheet_path.str_pad($_GET['id'], 4, "0", STR_PAD_LEFT).".pdf";
  header('Content-type: application/pdf');
  header('Content-Disposition: attachment; filename="' . $prefix . $_GET['id'] . '.pdf"');
  header('Content-Transfer-Encoding: binary');
  header('Content-Length: ' . filesize($scoresheetfilename));
  header('Accept-Ranges: bytes');
  ob_clean();
  flush();
  readfile($scoresheetfilename);
}
?>
