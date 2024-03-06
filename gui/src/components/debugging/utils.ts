import rms from '@/api/rms'
import type { Job } from '@/api/types'

export const getJobs = async (): Promise<Job[]> => {
  const master = await rms.loadPluginDotMaster()
  return master.parameters
}
