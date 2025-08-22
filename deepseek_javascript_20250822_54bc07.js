// استيراد المكتبات المطلوبة
const express = require('express');
const cors = require('cors');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

// إنشاء تطبيق Express
const app = express();
const port = process.env.PORT || 3000;

// إعداد middleware للسماح بالاتصال من أي نطاق (CORS)
app.use(cors());
// إعداد middleware لفهم البيانات المرسلة بصيغة JSON
app.use(express.json());

// تهيئة Gemini API باستخدام المفتاح من متغيرات البيئة
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// مسار للشات - هذا المسار يستقبل رسائل المستخدم ويرد باستخدام Gemini
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'الرسالة مطلوبة' });
    }

    const model = genAI.getGenerativeModel({ model: "gemini-pro" });
    const result = await model.generateContent(message);
    const response = await result.response;
    const text = response.text();

    res.json({ reply: text });
  } catch (error) {
    console.error('Error with Gemini API:', error);
    res.status(500).json({ error: 'حدث خطأ أثناء معالجة طلبك' });
  }
});

// مسار للتحقق من أن الخادم يعمل بشكل صحيح
app.get('/health', (req, res) => {
  res.json({ status: 'OK', message: 'الخادم يعمل بشكل طبيعي' });
});

// بدء تشغيل الخادم على المنفذ المحدد
app.listen(port, () => {
  console.log(`الخادم يعمل على المنفذ ${port}`);
});