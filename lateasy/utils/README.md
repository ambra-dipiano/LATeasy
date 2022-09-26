# Istruzioni per lanciare gli script

Le variabili d'ambiente usate negli esempi di questo README sono:

```bash
export PYCODE=/data01/projects/IGRJ17354-3255/FERMI/pycode
export DATA=/data01/projects/IGRJ17354-3255/FERMI/LC
```

## collectNPY.py
Questo script permette la raccolta di una serie di parametri a partire dagli output npy di un'analisi. Se l'analisi è composta da bin (es lightcurve) oltre a raccogliere i dati dei singoli periodi effettua un merge di tutti i risultati. 
Un secondo output con le detection sopra una soglia di TS viene creato contestualmente al merge.

### Output
Nella stessa folder degli output file.npy viene salvato il .txt della singola run di analysis. Nella cartella LC viene salvato il merge di tutte le run appartenenti ad una data analisi, più l'output contenente solo le detection sopra una data soglia di TS

### Istruzioni esecuzione
Dalla folder "parent" di cui si vogliono raccogliere i risultati di ogni analisi contenuta. 

```bash
python $PYCODE/collectNPY.py -f $DATA/ANALYSIS_FOLDER -t type
```
oppure
```bash
python $PYCODE/collectNPY.py --folder $DATA/ANALYSIS_FOLDER --type type
```

Dove type può essere LC/SED/ROI/LOC

### Esempio

```bash
python $PYCODE/collectNPY.py -f $DATA/TEST -t SED
```

## collectBIN.py
Questo script permette la raccolta di una serie di parametri a partire dagli output npy di un'analisi di un singolo bin. Se l'analisi è composta da bin (es lightcurve) lo script deve essere lanciato per ogni bin, e non provvede al merging di tutte le informazioni.

### Output
Nella stessa folder degli output file.npy viene salvato il .txt della singola run di analysis, con suffisso *_collected.txt al file di output.

### Istruzioni esecuzione
E' necessario specificare il file di cui si vuole raccogliere i dati.

```bash
python $PYCODE/collecBIN.py -f $DATA/TEST/TEST/file.npy -t type
```
oppure
```bash
python $PYCODE/collecBIN.py --folder $DATA/TEST/TEST/file.npy --type type
```

Dove type può essere LC/SED/ROI/LOC

### Esempio

```bash
python $PYCODE/collecBIN.py -f $DATA/TEST/TEST/roi2_optimize.npy -t ROI
```

## slurmIndexMonths.py
Questo script rinomina tutti i log slurm-IDJOB.out in slurm-MONTH.out contenuti in una cartella d'analisi.

### Istruzioni d'esecuzione

```bash
python $PYCODE/slurmIndexMonths.py $DATA/FOLDER_ANALYSIS
```

### Esempio

```bash
python $PYCODE/slurmIndexMonths.py $DATA/YEARS5j
```

## collectLC.py
Questo script permette di estrarre i dati (tmin, tmax, ts, flux, flux_err, flux_ul95) dagli output della gta.lightcurve. 

### Output
1) curve di luce di ogni mese, salvate nella folder del mese (igrj17354-3255_lightcurve_collected.txt) 
2) curva di luce totale, salvata nella folder dell'analisi (igrj17354-3255_lightcurve_fullLC.txt) 
3) log contenente una lista dei mesi in cui dovesse mancare l'output della lightcurve, salvato in LC/ (es: YEARS5h_collectLC.log)

### Istruzioni d'esecuzione

```bash
python $PYCODE/collectLC.py $DATA/FOLDER_ANALYSIS
```

### Esempio

```bash
python $PYCODE/collectLC.py $DATA/YEARS5j
```

## collectLCdata.py
Questo script data una LC già raccolta, estrae solamente le detection sopra una data soglia di TS.
Al tmin, tmax in MET delle detection vengono anche aggiunti tmin, tmax in MJD.\
**NB: è necessario attivare prima l'ambiente fermipy3 o un altro ambiente che contenga python3 e pandas (python2 ha problemi di compatibilità con la funzione round() che non mi sono del tutto chiari)**

### Output
Nella stessa folder della igrj17354-3255_lightcurve_fullLC.txt, viene salvato il file igrj17354-3255_lightcurve_aboveXts.py dove X è il valore di soglia in TS.

### Istruzioni esecuzione

```bash
python $PYCODE/collectLCdata.py $DATA/FOLDER_ANALYSIS [TS_THRESH]
```

Se TS_THRESH non viene specificato, il default è 9.

### Esempio

```bash
python $PYCODE/collectLCdata.py $DATA/YEARS5j 
```

Oppure

```bash
python $PYCODE/collectLCdata.py YEARS5j 25
```


## collectLOC.py
Questo script permette di estrarre i dati (ra, ra_err, dec, dec_err, ra_preloc, dec_preloc, pos_offset, pos_r95) dagli output della gta.localize se esistente. 

### Output
1) output di ogni mese, salvati nella folder del mese (*_collected.txt) 
2) output totale, salvato nella folder dell'analisi (*_fullLOC.txt) 
3) log contenente una lista dei mesi in cui l'output è presente, salvato in LC/ (es: YEARS5h_collectLOC.log)

### Istruzioni d'esecuzione

```bash
python $PYCODE/collectLC.py $DATA/FOLDER_ANALYSIS
```

### Esempio

```bash
python $PYCODE/collectLC.py $DATA/YEARS5j
```
