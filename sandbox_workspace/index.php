<?php
// Simple vulnerable login demo (CTF)

$flag = "CTF{sql_bypass_success}";

$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';

echo "<h2>Login Page</h2>";

if ($username == "admin" && $password == "admin123") {
    echo "Welcome admin!<br>";
    echo "FLAG: " . $flag;
} else {
    echo "<form method='POST'>
        Username: <input name='username'><br>
        Password: <input name='password' type='password'><br>
        <button type='submit'>Login</button>
    </form>";
}
?>
