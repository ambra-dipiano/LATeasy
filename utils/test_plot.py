import matplotlib
gui_env = [i for i in matplotlib.rcsetup.interactive_bk]
non_gui_backends = matplotlib.rcsetup.non_interactive_bk
#print("Non Gui backends are:", non_gui_backends)
#print("Gui backends are:", gui_env)

print('NON GUI')
for gui in non_gui_backends:
    print("testing", gui)
    try:
        matplotlib.use(gui,warn=False, force=True)
        from matplotlib import pyplot as plt
        print(gui, "Is Available")
    except:
        print(gui, "Not found")

#matplotlib.use('agg')
#global plt
#import matplotlib.pyplot as plt
#plt.switch_backend('agg')

print('GUI')
for gui in gui_env:
    print("testing", gui)
    try:
        matplotlib.use(gui,warn=False, force=True)
        from matplotlib import pyplot as plt
        print(gui, "Is Available")
    except:
        print(gui, "Not found")


