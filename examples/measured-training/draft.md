# mac-local-training v0.1.0 — draft

## English

I ran a local software check of all-layer LoRA and rotating layer updates on an Apple M1. The model was tiny and randomly initialized. In this short experiment, rotating reduced resident optimizer state, while the process RSS high-water mark increased. Each layer received fewer updates in the rotating run; equal trainer-step counts do not mean an equal per-layer update budget. The figures below come from the saved benchmark summary.

- Random seed / البذرة العشوائية: 17.
- Trainer steps — all / خطوات تدريب كل الطبقات: 40.
- Trainer steps — rotating / خطوات تدريب التدوير: 40.
- Updates to layer 0 — all / تحديثات الطبقة 0 عند تدريب كل الطبقات: 40.
- Updates to layer 0 — rotating / تحديثات الطبقة 0 عند التدوير: 10.
- Peak resident optimizer state — all / ذروة ذاكرة حالة المحسّن لكل الطبقات: 14348 bytes.
- Peak resident optimizer state — rotating / ذروة ذاكرة حالة المحسّن عند التدوير: 3596 bytes.
- Process RSS high-water — all / ذروة RSS لكل الطبقات: 105185280 bytes.
- Process RSS high-water — rotating / ذروة RSS عند التدوير: 110051328 bytes.

Limits: One seed and one short run per strategy on a tiny random model, using synthetic bilingual templates with overlap across the training and validation splits. Full base weights stay resident. Lower optimizer state did not reduce total process RSS here. This is a software check, not a claim of cybersecurity accuracy, useful model quality, a large-model memory result, a new training method, or a matched-compute performance comparison.

Code: https://github.com/megern/mac-local-training

## العربية

نفذت تجربة محلية للتحقق من عمل التدريب على Apple M1، بمقارنة تحديث طبقات LoRA كلها وتحديثها بالتدوير. النموذج صغير ومهيأ عشوائيًا. في هذه التجربة القصيرة انخفضت ذاكرة حالة المحسّن مع التدوير، بينما زادت ذروة ذاكرة العملية RSS. حصلت كل طبقة على تحديثات أقل مع التدوير؛ تساوي عدد خطوات التدريب لا يعني تساوي عدد تحديثات كل طبقة. الأرقام التالية مأخوذة من ملخص القياس المحفوظ.

- Random seed / البذرة العشوائية: 17.
- Trainer steps — all / خطوات تدريب كل الطبقات: 40.
- Trainer steps — rotating / خطوات تدريب التدوير: 40.
- Updates to layer 0 — all / تحديثات الطبقة 0 عند تدريب كل الطبقات: 40.
- Updates to layer 0 — rotating / تحديثات الطبقة 0 عند التدوير: 10.
- Peak resident optimizer state — all / ذروة ذاكرة حالة المحسّن لكل الطبقات: 14348 bytes.
- Peak resident optimizer state — rotating / ذروة ذاكرة حالة المحسّن عند التدوير: 3596 bytes.
- Process RSS high-water — all / ذروة RSS لكل الطبقات: 105185280 bytes.
- Process RSS high-water — rotating / ذروة RSS عند التدوير: 110051328 bytes.

حدود التجربة: بذرة عشوائية واحدة وتشغيل قصير واحد لكل طريقة، على نموذج صغير عشوائي وبيانات ثنائية اللغة اصطناعية تتداخل قوالبها بين التدريب والتحقق. تبقى أوزان النموذج الأساسية في الذاكرة. انخفاض ذاكرة المحسّن لم يخفض ذاكرة العملية الكلية RSS في هذه التجربة. هذه تجربة للتحقق من عمل البرنامج، وليست دليلًا على جودة نموذج مفيد أو دقة سيبرانية أو ملاءمة نموذج كبير للذاكرة، ولا ادعاء بطريقة تدريب جديدة أو مقارنة أداء بميزانية تحديثات متساوية.

الكود: https://github.com/megern/mac-local-training

---
Draft for human review. No post has been published.
