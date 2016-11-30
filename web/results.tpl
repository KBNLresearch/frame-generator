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

    <h2>Frames generated:</h2>

    <ol>
        % for i, k in enumerate(keywords):
        <li>{{k[0]}}: {{', '.join([f[0] for f in frames[i]])}}</li>
        % end
    </ol>

</body>
</html>
