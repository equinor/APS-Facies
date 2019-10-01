import rms from '@/api/rms'
import { makeSelectionModule } from '@/store/modules/parameters/utils'

export default makeSelectionModule((): Promise<string> => rms.projectDirectory())
