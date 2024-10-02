import json
import boto3
import base64
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    path = event.get('rawPath', '/')
    method = event.get('requestContext', {}).get('http', {}).get('method', '')

    if path == '/' and method == 'GET':
        # Serve a interface web
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Upload de Arquivo</title>
            </head>
            <body>
                <h1>Upload de Arquivo para S3</h1>
                <input type="file" id="fileInput"><br><br>
                <button onclick="uploadFile()">Fazer Upload</button>

                <script>
                    async function uploadFile() {
                        const fileInput = document.getElementById('fileInput');
                        const file = fileInput.files[0];
                        if (!file) {
                            alert('Por favor, selecione um arquivo.');
                            return;
                        }

                        const reader = new FileReader();
                        reader.onload = async function(event) {
                            const base64String = event.target.result.split(',')[1];

                            const response = await fetch('/upload', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/octet-stream',
                                    'file-name': file.name
                                },
                                body: base64String
                            });

                            const result = await response.json();
                            alert(result);
                        };
                        reader.readAsDataURL(file);
                    }
                </script>
            </body>
            </html>
            '''
        }
    elif path == '/upload' and method == 'POST':
        # Processa o upload do arquivo
        file_content = base64.b64decode(event['body'])
        file_name = event['headers'].get('file-name', 'uploaded_file')

        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)

        return {
            'statusCode': 200,
            'body': json.dumps('Arquivo carregado com sucesso!')
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('Rota não encontrada.')
        }
