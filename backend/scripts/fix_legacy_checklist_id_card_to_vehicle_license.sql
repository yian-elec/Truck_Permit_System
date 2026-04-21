-- 一次性修正：舊版草稿檢核列為 id_card（身分證件），與申請端上傳之
-- attachment_type=vehicle_license_copy 不一致，導致送件永遠 missing_required_attachments。
-- 將該列改為 vehicle_license_copy，並依是否已有對應附件重算 is_satisfied。
--
-- 執行（依環境調整連線）： psql $DATABASE_URL -f scripts/fix_legacy_checklist_id_card_to_vehicle_license.sql

UPDATE application.checklists AS c
SET
  item_code = 'vehicle_license_copy',
  item_name = '行車執照影本（拖車使用證）',
  is_required = true,
  is_satisfied = EXISTS (
    SELECT 1
    FROM application.attachments AS a
    WHERE a.application_id = c.application_id
      AND a.attachment_type = 'vehicle_license_copy'
      AND lower(trim(a.status)) = 'uploaded'
  )
WHERE c.item_code = 'id_card';
