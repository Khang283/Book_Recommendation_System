## Cài đặt
Tạo file venv
```
    python -m venv .venv
```

Activate venv
```
    .venv/Scripts/activate
```

Cài các requirements
``` 
    pip install -r requirements.txt
```

Download các file cần thiết trên drive và đặt theo đường dẫn
```bash
 data
  ├── W2v
  │   ├── GoogleNews-vectors-negative300.bin.gz
  │   └── stopwords.txt
  ├── als_prediction.csv
  ├── books.csv
  ├── knn_prediction.csv
  └── rawdata
      ├── metadata.json
      ├── ratings.json
      ├── tag_count.json
      ├── tags.json
      └── users.json
```


## Chạy server
```
    flask --app flaskr run --debug
```
