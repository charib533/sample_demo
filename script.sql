DECLARE
  TYPE t_vz_id IS TABLE OF uuidb.ui_settings.vz_id%TYPE;
  TYPE t_ui_object_name IS TABLE OF uuidb.ui_settings.ui_object_name%TYPE;
  TYPE t_favorites IS TABLE OF CLOB;
  v_vz_id t_vz_id;
  v_ui_object_name t_ui_object_name;
  v_favorites t_favorites;
  v_count INTEGER;
  CURSOR c_data IS
  SELECT
    vz_id,
    ui_object_name,
    JSON_QUERY(setting, '$.links[1]') AS favorites
  FROM
    uuidb.ui_settings
  WHERE
    JSON_VALUE(setting, '$.links[1].label') = 'Favorites';
BEGIN
  OPEN c_data;
  FETCH c_data BULK COLLECT INTO v_vz_id, v_ui_object_name, v_favorites;

  FOR i IN 1..v_vz_id.COUNT LOOP
    SELECT COUNT(*) INTO v_count 
    FROM uuidb.menu_favorites 
    WHERE vz_id = v_vz_id(i) AND ui_object_name = v_ui_object_name(i);

    IF v_count = 0 THEN
      v_vz_id(i) := NULL;
    END IF;
  END LOOP;

  FORALL i IN 1..v_vz_id.COUNT
  INSERT INTO uuidb.menu_favorites (
    vz_id,
    ui_object_name, 
    setting, 
    last_modified_by, 
    last_modified_date
  ) VALUES (
    v_vz_id(i),
    v_ui_object_name(i), 
    v_favorites(i), 
    v_vz_id(i),
    sysdate
  );
  
  COMMIT;
EXCEPTION
  WHEN no_data_found THEN
    dbms_output.put_line('No Data Found for the given parameters.');
END;