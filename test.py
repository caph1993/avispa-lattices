import local_avispa_lattices as AL

non_mod = []
mod = []
dist = []
for L in AL.generation.iter_all_latices(4):
    if L.is_distributive:
        dist.append(L)
        L.show()
    elif L.is_modular:
        mod.append(L)
    else:
        non_mod.append(L)

print(f'{len(dist)} distributives')
print(f'{len(mod)} modulars')
print(f'{len(non_mod)} non-modulars')