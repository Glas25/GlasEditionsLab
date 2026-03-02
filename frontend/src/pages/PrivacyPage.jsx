import { Link } from "react-router-dom";
import { BookOpen, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur-sm border-b border-border">
        <div className="max-w-4xl mx-auto px-6 md:px-12">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary rounded-sm flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-serif text-xl font-semibold tracking-tight">GlasEditionsLab</span>
            </Link>
            <Link to="/">
              <Button variant="ghost" className="rounded-sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Retour
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 md:px-12 py-12">
        <h1 className="font-serif text-4xl font-bold mb-8">Politique de Confidentialité</h1>
        
        <div className="prose prose-stone max-w-none space-y-8">
          <p className="text-muted-foreground">Dernière mise à jour : Février 2026</p>

          <div className="bg-primary/5 p-6 rounded-sm border border-primary/20">
            <p className="m-0">
              <strong>Résumé :</strong> Nous collectons uniquement les données nécessaires au 
              fonctionnement du service. Vos livres vous appartiennent. Nous ne vendons pas 
              vos données. Vous pouvez demander la suppression de vos données à tout moment.
            </p>
          </div>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">1. Responsable du traitement</h2>
            <p>Le responsable du traitement des données personnelles est :</p>
            <div className="bg-stone-50 p-6 rounded-sm mt-4">
              <ul className="list-none space-y-2 m-0 p-0">
                <li><strong>Raison sociale :</strong> EI Glas25</li>
                <li><strong>Adresse :</strong> 1 Ter rue du Cotay, 25300 Arçon, France</li>
                <li><strong>SIRET :</strong> 520 388 166 00024</li>
                <li><strong>Email DPO :</strong> <a href="mailto:contact@glaseditionslab.com" className="text-primary hover:underline">contact@glaseditionslab.com</a></li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">2. Données collectées</h2>
            <p>
              Nous collectons différentes catégories de données selon votre utilisation du service :
            </p>
            
            <h3 className="font-semibold text-lg mt-6 mb-3">2.1 Données d'identification</h3>
            <table className="w-full border-collapse border border-stone-200 mt-4">
              <thead>
                <tr className="bg-stone-50">
                  <th className="border border-stone-200 p-3 text-left">Donnée</th>
                  <th className="border border-stone-200 p-3 text-left">Finalité</th>
                  <th className="border border-stone-200 p-3 text-left">Obligatoire</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-stone-200 p-3">Nom</td>
                  <td className="border border-stone-200 p-3">Personnalisation du compte</td>
                  <td className="border border-stone-200 p-3">Oui</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Email</td>
                  <td className="border border-stone-200 p-3">Authentification, communications</td>
                  <td className="border border-stone-200 p-3">Oui</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Mot de passe (hashé)</td>
                  <td className="border border-stone-200 p-3">Sécurité du compte</td>
                  <td className="border border-stone-200 p-3">Oui (sauf Google)</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Photo de profil</td>
                  <td className="border border-stone-200 p-3">Personnalisation (via Google)</td>
                  <td className="border border-stone-200 p-3">Non</td>
                </tr>
              </tbody>
            </table>

            <h3 className="font-semibold text-lg mt-6 mb-3">2.2 Données de paiement</h3>
            <p>
              <strong>Important :</strong> Nous n'avons jamais accès à vos informations 
              bancaires complètes. Les paiements sont traités par Stripe, qui stocke ces 
              données de manière sécurisée.
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>Identifiant client Stripe (référence anonyme)</li>
              <li>Historique des transactions (montant, date, statut)</li>
              <li>Type d'abonnement souscrit</li>
            </ul>

            <h3 className="font-semibold text-lg mt-6 mb-3">2.3 Données d'utilisation</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Livres créés (titre, idée, contenu des chapitres)</li>
              <li>Images de couverture générées</li>
              <li>Préférences de génération (genre, ton, nombre de chapitres)</li>
              <li>Dates de création et modification</li>
              <li>Statistiques d'utilisation (nombre de livres, mots générés)</li>
            </ul>

            <h3 className="font-semibold text-lg mt-6 mb-3">2.4 Données techniques</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li>Adresse IP (pour la sécurité)</li>
              <li>Type de navigateur et système d'exploitation</li>
              <li>Pages visitées et interactions</li>
              <li>Dates et heures de connexion</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">3. Finalités du traitement</h2>
            <p>Vos données sont utilisées pour :</p>
            
            <table className="w-full border-collapse border border-stone-200 mt-4">
              <thead>
                <tr className="bg-stone-50">
                  <th className="border border-stone-200 p-3 text-left">Finalité</th>
                  <th className="border border-stone-200 p-3 text-left">Base légale</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-stone-200 p-3">Création et gestion de votre compte</td>
                  <td className="border border-stone-200 p-3">Exécution du contrat</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Fourniture des services de génération</td>
                  <td className="border border-stone-200 p-3">Exécution du contrat</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Traitement des paiements</td>
                  <td className="border border-stone-200 p-3">Exécution du contrat</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Support client</td>
                  <td className="border border-stone-200 p-3">Exécution du contrat</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Prévention de la fraude</td>
                  <td className="border border-stone-200 p-3">Intérêt légitime</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Amélioration des services</td>
                  <td className="border border-stone-200 p-3">Intérêt légitime</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Conservation des factures</td>
                  <td className="border border-stone-200 p-3">Obligation légale</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">4. Durée de conservation</h2>
            <p>
              Conformément au RGPD, nous conservons vos données uniquement le temps nécessaire :
            </p>
            <table className="w-full border-collapse border border-stone-200 mt-4">
              <thead>
                <tr className="bg-stone-50">
                  <th className="border border-stone-200 p-3 text-left">Type de données</th>
                  <th className="border border-stone-200 p-3 text-left">Durée de conservation</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-stone-200 p-3">Données de compte</td>
                  <td className="border border-stone-200 p-3">Durée d'inscription + 3 ans après suppression</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Livres et contenus</td>
                  <td className="border border-stone-200 p-3">Durée d'inscription (supprimés avec le compte)</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Données de paiement</td>
                  <td className="border border-stone-200 p-3">10 ans (obligation comptable)</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Logs de connexion</td>
                  <td className="border border-stone-200 p-3">1 an</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">Cookies de session</td>
                  <td className="border border-stone-200 p-3">7 jours maximum</td>
                </tr>
              </tbody>
            </table>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">5. Partage des données</h2>
            <p>
              Nous ne vendons jamais vos données. Nous partageons certaines données avec 
              des prestataires de confiance, uniquement pour le fonctionnement du service :
            </p>

            <h3 className="font-semibold text-lg mt-6 mb-3">5.1 Stripe (paiements)</h3>
            <p>
              Stripe traite vos paiements de manière sécurisée. Ils reçoivent les informations 
              nécessaires au traitement des transactions.
            </p>
            <p className="mt-2">
              <a href="https://stripe.com/fr/privacy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                Politique de confidentialité Stripe →
              </a>
            </p>

            <h3 className="font-semibold text-lg mt-6 mb-3">5.2 Google (authentification et IA)</h3>
            <p>
              <strong>Google OAuth :</strong> Si vous vous connectez via Google, nous recevons 
              votre nom, email et photo de profil. Google ne reçoit pas d'informations sur 
              votre utilisation de nos services.
            </p>
            <p className="mt-4">
              <strong>Google Gemini (IA) :</strong> Les idées et paramètres que vous fournissez 
              sont envoyés à l'API Gemini pour la génération. Google ne stocke pas ces données 
              au-delà du traitement immédiat et ne les utilise pas pour entraîner ses modèles.
            </p>
            <p className="mt-2">
              <a href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                Politique de confidentialité Google →
              </a>
            </p>

            <h3 className="font-semibold text-lg mt-6 mb-3">5.3 Hébergement</h3>
            <p>
              Nos serveurs sont hébergés par Emergent Labs. Vos données sont stockées de 
              manière sécurisée sur des infrastructures conformes aux normes de sécurité.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">6. Transfert hors UE</h2>
            <p>
              Certains de nos prestataires (Stripe, Google) peuvent traiter des données en 
              dehors de l'Union Européenne. Ces transferts sont encadrés par :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>Les clauses contractuelles types de la Commission Européenne</li>
              <li>Le Data Privacy Framework (pour les transferts vers les États-Unis)</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">7. Vos droits</h2>
            <p>
              Conformément au RGPD, vous disposez des droits suivants sur vos données :
            </p>
            
            <div className="grid md:grid-cols-2 gap-4 mt-6">
              <div className="bg-stone-50 p-4 rounded-sm">
                <h4 className="font-semibold mb-2">📋 Droit d'accès</h4>
                <p className="text-sm">Obtenir une copie de toutes vos données personnelles</p>
              </div>
              <div className="bg-stone-50 p-4 rounded-sm">
                <h4 className="font-semibold mb-2">✏️ Droit de rectification</h4>
                <p className="text-sm">Corriger des données inexactes ou incomplètes</p>
              </div>
              <div className="bg-stone-50 p-4 rounded-sm">
                <h4 className="font-semibold mb-2">🗑️ Droit à l'effacement</h4>
                <p className="text-sm">Demander la suppression de vos données ("droit à l'oubli")</p>
              </div>
              <div className="bg-stone-50 p-4 rounded-sm">
                <h4 className="font-semibold mb-2">📦 Droit à la portabilité</h4>
                <p className="text-sm">Recevoir vos données dans un format structuré</p>
              </div>
              <div className="bg-stone-50 p-4 rounded-sm">
                <h4 className="font-semibold mb-2">⛔ Droit d'opposition</h4>
                <p className="text-sm">Vous opposer au traitement de vos données</p>
              </div>
              <div className="bg-stone-50 p-4 rounded-sm">
                <h4 className="font-semibold mb-2">⏸️ Droit à la limitation</h4>
                <p className="text-sm">Limiter temporairement le traitement</p>
              </div>
            </div>

            <p className="mt-6">
              Pour exercer ces droits, contactez-nous à : 
              <a href="mailto:contact@glaseditionslab.com" className="text-primary hover:underline ml-1">contact@glaseditionslab.com</a>
            </p>
            <p className="mt-2">
              Nous répondrons à votre demande dans un délai de <strong>30 jours</strong>.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">8. Sécurité des données</h2>
            <p>
              Nous mettons en œuvre des mesures techniques et organisationnelles pour 
              protéger vos données :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li><strong>Chiffrement :</strong> Toutes les communications sont chiffrées (HTTPS/TLS)</li>
              <li><strong>Mots de passe :</strong> Hashés avec bcrypt (jamais stockés en clair)</li>
              <li><strong>Authentification :</strong> Tokens JWT sécurisés avec expiration</li>
              <li><strong>Accès :</strong> Accès restreint aux bases de données</li>
              <li><strong>Monitoring :</strong> Surveillance des accès anormaux</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">9. Cookies</h2>
            <p>
              GlasEditionsLab utilise uniquement des cookies essentiels au fonctionnement :
            </p>
            <table className="w-full border-collapse border border-stone-200 mt-4">
              <thead>
                <tr className="bg-stone-50">
                  <th className="border border-stone-200 p-3 text-left">Cookie</th>
                  <th className="border border-stone-200 p-3 text-left">Finalité</th>
                  <th className="border border-stone-200 p-3 text-left">Durée</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-stone-200 p-3">auth_token</td>
                  <td className="border border-stone-200 p-3">Authentification</td>
                  <td className="border border-stone-200 p-3">7 jours</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">session_token</td>
                  <td className="border border-stone-200 p-3">Session utilisateur</td>
                  <td className="border border-stone-200 p-3">Session</td>
                </tr>
                <tr>
                  <td className="border border-stone-200 p-3">cookie_consent</td>
                  <td className="border border-stone-200 p-3">Préférences cookies</td>
                  <td className="border border-stone-200 p-3">1 an</td>
                </tr>
              </tbody>
            </table>
            <p className="mt-4">
              Ces cookies sont strictement nécessaires et ne peuvent pas être désactivés.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">10. Mineurs</h2>
            <p>
              GlasEditionsLab n'est pas destiné aux personnes de moins de 16 ans. Nous ne 
              collectons pas sciemment de données concernant des mineurs. Si nous découvrons 
              qu'un mineur a créé un compte, nous supprimerons ses données.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">11. Modifications</h2>
            <p>
              Nous pouvons modifier cette politique de confidentialité à tout moment. En cas 
              de modification substantielle, nous vous en informerons par email ou via une 
              notification sur le site.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">12. Réclamation</h2>
            <p>
              Si vous estimez que le traitement de vos données constitue une violation du RGPD, 
              vous pouvez introduire une réclamation auprès de la CNIL :
            </p>
            <div className="bg-stone-50 p-6 rounded-sm mt-4">
              <p><strong>Commission Nationale de l'Informatique et des Libertés (CNIL)</strong></p>
              <p className="mt-2">3 Place de Fontenoy, TSA 80715</p>
              <p>75334 Paris Cedex 07</p>
              <p className="mt-2">
                <a href="https://www.cnil.fr" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                  www.cnil.fr
                </a>
              </p>
            </div>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">13. Contact</h2>
            <p>
              Pour toute question relative à cette politique de confidentialité ou pour 
              exercer vos droits :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li><strong>Email :</strong> <a href="mailto:contact@glaseditionslab.com" className="text-primary hover:underline">contact@glaseditionslab.com</a></li>
              <li><strong>Courrier :</strong> EI Glas25, 1 Ter rue du Cotay, 25300 Arçon, France</li>
            </ul>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 border-t border-border mt-12">
        <div className="max-w-4xl mx-auto px-6 md:px-12 text-center text-sm text-muted-foreground">
          © 2025 GlasEditionsLab - EI Glas25
        </div>
      </footer>
    </div>
  );
}
