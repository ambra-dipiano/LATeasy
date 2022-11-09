# Istruzioni per lanciare gli script

Le variabili d'ambiente usate negli esempi di questo README sono:

```bash
export PYCODE=/data01/projects/IGRJ17354-3255/FERMI/pycode
export DATA=/data01/projects/IGRJ17354-3255/FERMI/LC
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
