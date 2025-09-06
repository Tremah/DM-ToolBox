rm /media/work/workspace/repo/DMToolBox_Desktop/.venv/data/input/osr_armor_weapons_equipment/csv/*
libreoffice25.2 --convert-to csv:"Text - txt - csv (StarCalc)":59,34,UTF8,1,,0,false,true,false,false,false,4 "/media/work/workspace/dnd/docs/osr_armor_weapons_equipment.ods" --outdir "/media/work/workspace/repo/DMToolBox_Desktop/.venv/data/input/osr_armor_weapons_equipment/csv"
cd /media/work/workspace/repo/DMToolBox_Desktop/.venv/data/input/osr_armor_weapons_equipment/csv/
mv *csv osr_armor_weapons_equipment_export.csv

