import asyncio
import sys
from typing import NoReturn

# --- Dependencies (Imported from previously migrated modules) ---
from .banner  import BannerService
from .makedict import MakeDictService
from ..latin_utils import PrefaceService,Config 
from ..support_utils import DeveloperParametersService

async def main() -> NoReturn:
    """
    Main entry point for the MAKEDICT utility.
    Maps to 'procedure MAKEDICT_MAIN'.
    """
    try:
        # 1. Initialize core infrastructure services
        # Note: PrefaceConfig would ideally be loaded from a global CONFIG package
        config = Config(suppress_preface=False)
        preface = PrefaceService()
        preface.set_config(config)
        dev_params = DeveloperParametersService()
        
        # 2. Instantiate component services
        banner_service = BannerService(preface)
        makedict_service = MakeDictService(porting=False)

        # 3. Execution flow
        # Ada: BANNER.BANNER_MAKEDICT;
        banner_service.banner_makedict()
        
        # Ada: MAKEDICT;
        makedict_service.run()

    except Exception as e:
        print(f"\nMAKEDICT_MAIN terminated on exception: {e}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    # Standard entry point for the standalone utility
    asyncio.run(main())
