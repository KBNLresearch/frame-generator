<!DOCTYPE html>
<html>
<head>
    <title>Frame Generator</title>
    <meta charset="UTF-8">

    <style>
        /* * {margin: 0; padding: 0; border: 0;} */
        body {font-family: helvetica, sans-serif; color: #333; overflow-y: scroll;}
    </style>

</head>
<body>

    <h1>Frame Generator</h1>

    <form id="form" method="post" action="" enctype="multipart/form-data">

        Select documents:<br>
        <input type="file" name="doc_files" multiple>
        <br><br>

        Select stop word files:<br>
        <input type="file" name="stop_files" multiple>
        <br><br>

        Keyword tags:<br>
        <input type="checkbox" name="ktag1" value="ADJ">Adjective (ADJ)<br>
        <!-- <input type="checkbox" name="ktag2" value="BW">BW (Adverb)<br> -->
        <!-- <input type="checkbox" name="ktag3" value="LET">LET (Punctuation)<br> -->
        <!-- <input type="checkbox" name="ktag4" value="LID">LID (Determiner)<br> -->
        <input type="checkbox" name="ktag5" value="N" checked>Noun (N)<br>
        <input type="checkbox" name="ktag6" value="SPEC" checked>Names(SPEC)<br>
        <!-- <input type="checkbox" name="ktag7" value="TSW">TSW (Interjection)<br> -->
        <!-- <input type="checkbox" name="ktag8" value="TW">TW (Numerator)<br> -->
        <!-- <input type="checkbox" name="ktag9" value="VG">VG (Conjunction)<br> -->
        <!-- <input type="checkbox" name="ktag10" value="VNW">VNW (Pronoun)<br> -->
        <!-- <input type="checkbox" name="ktag11" value="VZ">VZ (Preposition)<br> -->
        <input type="checkbox" name="ktag12" value="WW">Verb (WW)<br>
        <br>

        Frame tags:<br>
        <input type="checkbox" name="ftag1" value="ADJ" checked>Adjective (ADJ)<br>
        <!-- <input type="checkbox" name="ftag2" value="BW">BW (Adverb)<br> -->
        <!-- <input type="checkbox" name="ftag3" value="LET">LET (Punctuation)<br> -->
        <!-- <input type="checkbox" name="ftag4" value="LID">LID (Determiner)<br> -->
        <input type="checkbox" name="ftag5" value="N">Noun (N)<br>
        <input type="checkbox" name="ftag6" value="SPEC">Names (SPEC)<br>
        <!-- <input type="checkbox" name="ftag7" value="TSW">TSW (Interjection)<br> -->
        <!-- <input type="checkbox" name="ftag8" value="TW">TW (Numerator)<br> -->
        <!-- <input type="checkbox" name="ftag9" value="VG">VG (Conjunction)<br> -->
        <!-- <input type="checkbox" name="ftag10" value="VNW">VNW (Pronoun)<br> -->
        <!-- <input type="checkbox" name="ftag11" value="VZ">VZ (Preposition)<br> -->
        <input type="checkbox" name="ftag12" value="WW">Verb (WW)<br>
        <br>

        Window size:<br>
        <select name="window_size">
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5" selected>5</option>
            <option value="6">6</option>
            <option value="7">7</option>
            <option value="8">8</option>
            <option value="9">9</option>
            <option value="10">10</option>
        </select>
        <br><br>

        Window direction:<br>
        <select name="window_direction">
            <option value="left">Left</option>
            <option value="right">Right</option>
            <option value="">Both</option>
        </select>
        <br><br>

        <input type="submit" value="Generate frames"><br>
    </form>

</body>
</html>
