from pathlib import Path
from typing import Any
import datetime
import cProfile
import pstats
import os

def profile(callable: type, *args: tuple) -> Any:
    with cProfile.Profile() as profile: # Profiling the contents of the with block
        returnval = callable(*args)     # Calling the callable with the args

    # Naming the profile file in the format "profile_{hour}-{minute}-{second}.prof"
    statfile = Path(os.path.join("profiles", str(datetime.datetime.now().strftime("profile_%H-%M-%S")) + ".prof"))
    if not (statfile_dirpath := statfile.parent).exists():
        statfile_dirpath.mkdir() # Creating the dirpath of the statfile (ex. "build/profiles") if they do not exist
    stats = pstats.Stats(profile).sort_stats(pstats.SortKey.TIME) # Sorting the stats from highest time to lowest
    stats.dump_stats(filename=str(statfile)) # Saving the stats to a profile file
    stats.print_stats()                      # Printing the stats
    print(f"\n\n Profile saved to: {str(statfile)}!\n\n")
    return returnval