"""
Establishes the Config class, mirroring the configurations object in the primemover api
any parameters that are not set upon init are generated according to the
ConfigurationFunctions file.

J.L. 11.2020
"""

from src.worker.ConfigureProfile import Config


class GoogleConfig(Config):
    def update_config(self, results, new_location):
        """
        Update self according to results
        """
        if self.info is not None:
            self.history.pull_existing()

        if new_location is not None:
            self.location = new_location
        kappa_j_t = self.kappa

        for outlet in results:
            if self.kappa == 2:
                if not outlet['known']:
                    kappa_j_t = 1
                else:
                    kappa_j_t = 0

            self.pi = src.Preferences.political_orientation_pi_i_t(
                psi_i=self.psi, kappa_j_t_prev=kappa_j_t,
                pi_tilde_j_prev=outlet['pi'], pi_i_prev=self.pi)
        self.media = ConfigurationFunctions.update_media_outlets(
            outlets=self.media + results, alpha_tilde=self.alpha, pi=self.pi,
            tau_tilde_ij=self.tau, k=10)

        self.history.update_current_status()
        self.history.push()

