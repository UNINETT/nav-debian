<?php

/* 
 * auth.inc
 * - Denne inneholder authentiseringsrutinene for portalen til NAV.
 *
 *
 * Dette er et generelt bibliotek for å lagre sesjonsvariable,
 *	grunnen til at det er lagt i eget bibliotek er at php har endret litt
 *  på funksjonsnavnene for å lage sesjonsvariable og da er det enklere å endre
 *  ett sted enn 100. 
 */


/* 
 * Dette er en generell feilmeldingsklasse. 
 */
class Error {
  var $type;
  var $message;
  var $type_name;
  
  function Error ($errtype) {
    $this->type_name = array(gettext('Ukjent Feil'), gettext('Feil under innlogging'), 
    	gettext('Databasefeil'), gettext('Sikkerhetsfeil'), gettext('Lese/Skrive feil') );
    $this->type = $errtype;
  }

  function getHeader () {
    return $this->type_name[$this->type];
  }

  function setMessage ($msg) {
    $this->message = $msg;
  }

  function getHTML () {
    $html =  "<table width=\"100%\" class=\"feilWindow\"><tr><td class=\"mainWindowHead\"><h2>";
    $html .= $this->GetHeader();
    $html .= "</h2></td></tr>";
    $html .= "<tr><td><p>" . $this->message . "</td></tr></table>";
    return $html;
  }

}


global $login;
$login = false;

  /*
   * Already logged in
   */
if ( session_get('login') ) {
	$login = true;	
}
if (!isset($_ENV['REMOTE_USER'])) {
    $dbh->nyLogghendelse(session_get('uid'), 2, gettext("Logget ut") );
    $login = false;
    session_set('login', false);
}

/*
* First time login to NAVuser..
*/
if (isset($_ENV['REMOTE_USER'] ) AND
	( session_get('login') == false  OR 
		(session_get('login') AND (session_get('bruker') != $_ENV['REMOTE_USER']) 
		)
	) ) {

	// echo "Bruker:" . session_get('bruker') . ":   ENV:" . $_ENV['REMOTE_USER'] . ":";

    $username = $_ENV['REMOTE_USER'];

    $querystring = "
SELECT Account.id AS aid, Preference.admin, ap.value 
FROM Preference, Account 
	LEFT OUTER JOIN (
		SELECT accountid, property, value FROM AccountProperty WHERE property = 'language' 
	) AS ap ON 
    (Account.id = ap.accountid) 
WHERE (Account.login = '$username') AND 
    (Account.id = Preference.accountid) ";

   //echo "<p>Query: " . $querystring;

    if (! $query = pg_exec($dbh->connection, $querystring)  ) {
        $error = new Error(2);
        $error->message = gettext("Feil med datbasespørring.");
    } else {
        if (pg_numrows($query) == 1) {
            if ( $data = pg_fetch_array($query, $row) ) {
                // INNLOGGING OK!!
                $foo =  gethostbyaddr (getenv ("REMOTE_ADDR") );
                $dbh->nyLogghendelse($data["aid"], 1, gettext("Logget inn fra ") . $foo);
                
                $bgr = $dbh->listBrukersGrupper($data["aid"], 0);
                $uadmin = 1;
                foreach ($bgr AS $bg) {
                	if ($bg[0] == 1) $uadmin = 100;
                	if ($bg[0] == 2) $uadmin = 0;
                }

				session_delete('uid');
				session_delete('admin');
				session_delete('lang');
				session_delete('bruker');
				session_delete('login');
				session_delete('action');
				session_delete('subaction');

//				session_destroy();

                session_set('uid', $data["aid"]);
                session_set('admin', $uadmin);
                session_set('lang', $data["value"]);
                session_set('bruker', $username);
                session_set('login', true);
                $login = true;
            } else {
                $error = new Error(2);
                $error->message = gettext("Noe feil skjedde når jeg prøvde å hente ut brukerid fra databasen.");
            }
        } else {
            $error = new Error(1);
            $error->message = gettext("Inkonsistens i databasen. Du er korrekt innlogget, men brukeren din er ikke konfigurert riktig for å kunne fungere med NAV Alert. Ta kontakt med systemadministrator.");
        }
    }
}




?>
