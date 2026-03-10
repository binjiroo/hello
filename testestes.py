tex1 = "tex"
tex2 = "tex"
tex3 = "tex"
tex4 = "tex2"

if tex1 == tex2 and tex1 == tex3 and tex1 == tex4:
    print("すべて同一です。")
elif tex1 == tex2 and tex3 == tex4:
    print("1と2が一致、3と4が一致")
elif tex1 == tex3 and tex2 == tex4:
    print("1と3が一致、2と4が一致")
elif tex1 == tex4 and tex2 == tex3:
    print("1と4が一致、2と3が一致")
elif tex1 == tex2:
    print("1と2のみ一致")
elif tex1 == tex3:
    print("1と3のみ一致")
elif tex1 == tex4:
    print("1と4のみ一致")
elif tex2 == tex3:
    print("2と3のみ一致")
elif tex2 == tex4:
    print("2と4のみ一致")
elif tex3 == tex4:
    print("3と4のみ一致")
else:
    print("一致しません。")