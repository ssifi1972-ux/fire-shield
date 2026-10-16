import os
from Bio import ExPASy
from Bio import SwissProt

def fetch_and_verify_protein(protein_id):
    """
    الوكيل الأول: يتصل ببنك UniProt، يسحب البيانات، ويتحقق من متسلسلة الأحماض الأمينية.
    """
    print(f"[وكيل البحث]: جاري الاتصال ببنك البيانات للمعرّف: {protein_id}...")
    try:
        # الاتصال ببنك بيانات SwissProt/UniProt العالمي
        handle = ExPASy.get_sprot_raw(protein_id)
        record = SwissProt.read(handle)
        
        # استخراج المتسلسلة النظيفة للأحماض الأمينية
        sequence = record.sequence
        protein_name = record.description.split(';')[0]
        
        print("[وكيل البحث]: تم العثور على البروتين بنجاح!")
        print(f"الاسم: {protein_name}")
        print(f"طول المتسلسلة: {len(sequence)} حمض أميني.")
        
        # التحقق الأولي من جودة المتسلسلة
        if "X" in sequence:
            print("[تحذير]: المتسلسلة تحتوي على أحماض أمينية غير محددة (X)!")
        
        return {
            "status": "success",
            "name": protein_name,
            "sequence": sequence
        }
        
    except Exception as e:
        print(f"[خطأ]: فشل وكيل البحث في جلب البيانات. السبب: {e}")
        return {"status": "error", "message": str(e)}

# تجربة الكود محلياً
if __name__ == "__main__":
    # يمكنك استبدال هذا المعرف (P02768 هو ألبومين المصل البشري كمثال للتجربة)
    # بـ ID الخاص بالبروتين الزراعي الذي صممته
    test_id = "P02768" 
    result = fetch_and_verify_protein(test_id)
    
    if result["status"] == "success":
        print(f"\nالمتسلسلة الجاهزة للتحليل ثلاثي الأبعاد:\n{result['sequence'][:60]}...")
