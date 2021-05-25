import cx_Freeze

executables = [cx_Freeze.Executable("game.py")]

cx_Freeze.setup(
    name="RISK",
    options={"build_exe": {"packages":["pygame"],
                           "include_files":[
                               "Stage.png",
                               "Map.png",
                               "Logo.png",
                               "Skip.png",
                               "Skip_active.png",
                               "Number_bg.png",
                               "Right.png",
                               "Right_active.png",
                               "Left.png",
                               "Left_active.png",
                               "Tick.png",
                               "Tick_active.png",
                               "Cross.png",
                               "Cross_active.png",
                               "Cardlist.png",
                               "Message_table.png",
                               "Cards.png",
                               "Cards_active.png",
                               "Button_generic_large.png",
                               "Button_generic_large_active.png",
                               "card.py",
                               "color.py",
                               "continent.py",
                               "node.py",
                               "path.py",
                               "player.py",
                               "roll.py",
                               "troop.py",
                           ]}},
    executables = executables

    )