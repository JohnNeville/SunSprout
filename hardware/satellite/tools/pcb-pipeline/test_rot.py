import os, subprocess

test_sch = '''(kicad_sch
	(version 20260306)
	(generator "eeschema")
	(generator_version "10.0")
	(uuid "11111111-2222-3333-4444-555555555555")
	(paper "A4")
	(lib_symbols
		(symbol "Jumper:SolderJumper_2_Bridged"
			(pin_numbers (offset 0) (hide yes))
			(pin_names (offset 0) (hide yes))
			(exclude_from_sim no)
			(in_bom yes)
			(on_board yes)
			(property "Reference" "JP" (at 0 1.27 0) (effects (font (size 1.27 1.27))))
			(property "Value" "SolderJumper_2_Bridged" (at 0 -1.27 0) (effects (font (size 1.27 1.27)) (hide yes)))
			(property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
			(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
			(symbol "SolderJumper_2_Bridged_0_1"
				(arc (start -1.27 -2.54) (mid 0 -1.27) (end 1.27 -2.54) (stroke (width 0) (type default)) (fill (type none)))
			)
			(symbol "SolderJumper_2_Bridged_1_1"
				(pin passive line (at -5.08 0 0) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
				(pin passive line (at 5.08 0 180) (length 2.54) (name "B" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
			)
		)
	)
	(symbol
		(lib_id "Jumper:SolderJumper_2_Bridged")
		(at 50.8 50.8 270)
		(unit 1)
		(exclude_from_sim no)
		(in_bom yes)
		(on_board yes)
		(dnp no)
		(uuid "22222222-3333-4444-5555-666666666666")
		(property "Reference" "JP11"
			(id 0)
			(at 54.61 50.8 0)
			(effects
				(font (size 1.27 1.27))
				(justify left)
			)
		)
		(property "Value" "SolderJumper_2_Bridged"
			(id 1)
			(at 50.8 50.8 0)
			(effects
				(font (size 1.27 1.27))
				(hide yes)
			)
		)
		(property "Footprint" "Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm"
			(id 2)
			(at 50.8 50.8 0)
			(effects
				(font (size 1.27 1.27))
				(hide yes)
			)
		)
		(pin "1" (uuid "33333333-4444-5555-6666-777777777777"))
		(pin "2" (uuid "44444444-5555-6666-7777-888888888888"))
		(instances
			(project "test"
				(path "/11111111-2222-3333-4444-555555555555"
					(reference "JP11")
					(unit 1)
				)
			)
		)
	)
	(wire (pts (xy 50.8 45.72) (xy 50.8 35.56))
		(stroke (width 0) (type default))
		(uuid "55555555-6666-7777-8888-999999999999")
	)
	(wire (pts (xy 50.8 55.88) (xy 50.8 66.04))
		(stroke (width 0) (type default))
		(uuid "66666666-7777-8888-9999-000000000000")
	)
)
'''

sch_path = os.path.join(os.path.dirname(__file__), "test_rot.kicad_sch")
with open(sch_path, "w", encoding="utf-8") as f:
    f.write(test_sch)
print("Wrote", sch_path)
