from mido import MidiFile


SCALE = 12
MAJOR = []
MINOR = []
CONNECT = [3,4,5]
tonnetz = [[] for _ in range(SCALE)]
for i in range(SCALE):
    MAJOR.append([i, (i + 4) % 12, (i + 7) % 12])
    MINOR.append([i, (i + 3) % 12, (i + 7) % 12])
    for j in CONNECT:
        tonnetz[i].append((i + j) % SCALE)
        tonnetz[i].append((i - j + 12) % 12)

import os
names = []
diags = []
full_diags = []
directory = './classical_example'
for filename in os.listdir(directory):
    s = directory + '/' + filename
    mid = MidiFile(s)
    note_len = [0] * SCALE
    note_last = [0] * SCALE
    f = filename + '.diag'
    for track in mid.tracks:
        time = 0
        for msg in track:
            if (msg.type == 'note_on') and (msg.velocity != 0):
                note_last[(msg.note - 21) % SCALE] = time
            elif (msg.type == 'note_off') or ((msg.type == 'note_on') and (msg.velocity == 0)):
                note_len[(msg.note - 21) % SCALE] += time - note_last[(msg.note - 21) % SCALE]
            time += msg.time

    import gudhi
    st = gudhi.SimplexTree()
    for i in range(SCALE):
        st.insert([i], filtration=note_len[i])
        for j in tonnetz[i]:
            if j > i:
                st.insert([i, j], filtration = max(note_len[i], note_len[j]))

    
    for cur in MINOR:
        st.insert(cur, filtration = max(note_len[cur[0]], note_len[cur[1]], note_len[cur[2]]))

    for cur in MAJOR:
        st.insert(cur, filtration = max(note_len[cur[0]], note_len[cur[1]], note_len[cur[2]]))
    st.persistence()
    cur_set = []
    cur_set.append(filename)
    cur_set.append(st.persistence())
    full_diags.append(cur_set)
    st.write_persistence_diagram(f)

for cur_diag in full_diags:
    closed = 0
    opn = 0
    degree = [0] * 2
    for homology in cur_diag[1]:
            degree[homology[0]] += 1
            timers = homology[1]
            if (str(timers[1]) == 'inf'):
                opn += 1
            else:
                closed += 1

    print('name: ', cur_diag[0][:-4], '\n homologies of degree Zero and one:', *degree, '\n stayng homologies: ',  opn, 'deceased homologies: ' ,closed)
    print('full_homologies: ', cur_diag[1]) 
