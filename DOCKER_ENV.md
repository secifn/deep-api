# 🐳 การใช้ Environment Variables กับ Docker

**คำแนะนำ:** อย่าใส่ไฟล์ `.env1` เข้าไปใน Docker Image  
ให้ส่งค่าผ่าน **Environment** ตอนรัน container แทน เพื่อไม่ให้ secret รั่วไหล

---

## วิธีส่งค่าให้ Container

### วิธีที่ 1: ใช้ --env-file (แนะนำ)

```bash
docker run -d \
  --env-file /path/to/.env1 \
  your-image-name
```

ไฟล์ `.env1` อยู่บน host เท่านั้น **ไม่ถูก copy เข้า image**

---

### วิธีที่ 2: ใช้ docker-compose

ใน `docker-compose.yml`:

```yaml
services:
  report:
    image: your-report-image
    env_file:
      - .env1
    # หรือระบุทีละตัว:
    # environment:
    #   DEEPINSTINCT_URL: ${DEEPINSTINCT_URL}
    #   TOKENS_KEY: ${TOKENS_KEY}
    #   MATTERMOST_WEBHOOK_URL: ${MATTERMOST_WEBHOOK_URL}
    #   ...
```

รัน: `docker-compose --env-file .env1 up -d`

---

### วิธีที่ 3: ส่งทีละตัวด้วย -e

```bash
docker run -d \
  -e DEEPINSTINCT_URL="https://..." \
  -e TOKENS_KEY="eyJ..." \
  -e MATTERMOST_WEBHOOK_URL="https://..." \
  -e REPORT_SERVER_URL="https://..." \
  -e IT_PARCEL_API_URL="https://..." \
  -e IT_PARCEL_TOKEN="eyJ..." \
  your-image-name
```

---

## ไฟล์ที่เกี่ยวข้อง

- **`.dockerignore`** – กันไม่ให้ `.env1` ถูก copy ตอน `docker build`
- **`.gitignore`** – มี `.env1` อยู่แล้ว ไม่ให้ commit ขึ้น git

---

**สรุป:** ใช้ `.env1` แค่บน host แล้วส่งเข้า container ผ่าน `--env-file` หรือ `environment` ใน compose ไม่ต้อง copy ไฟล์เข้า image.
