import { Link } from "react-router-dom";
import { BookOpen, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function CGVPage() {
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
        <h1 className="font-serif text-4xl font-bold mb-8">Conditions Générales de Vente</h1>
        
        <div className="prose prose-stone max-w-none space-y-8">
          <p className="text-muted-foreground">Dernière mise à jour : Février 2026</p>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 1 - Objet et champ d'application</h2>
            <p>
              Les présentes Conditions Générales de Vente (ci-après « CGV ») régissent les 
              relations contractuelles entre EI Glas25 (ci-après « le Vendeur ») et toute 
              personne physique ou morale (ci-après « le Client ») souhaitant effectuer un 
              achat via le site GlasEditionsLab.
            </p>
            <p className="mt-4">
              Les présentes CGV s'appliquent à toutes les ventes de services d'abonnement 
              et de crédits de génération de livres. Le Client déclare avoir pris connaissance 
              des présentes CGV avant de passer commande.
            </p>
            <p className="mt-4">
              La validation de la commande vaut acceptation sans restriction ni réserve des 
              présentes CGV.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 2 - Identité du Vendeur</h2>
            <div className="bg-stone-50 p-6 rounded-sm">
              <ul className="list-none space-y-2 m-0 p-0">
                <li><strong>Raison sociale :</strong> EI Glas25 (Entreprise Individuelle)</li>
                <li><strong>Siège social :</strong> 1 Ter rue du Cotay, 25300 Arçon, France</li>
                <li><strong>SIRET :</strong> 520 388 166 00024</li>
                <li><strong>Email :</strong> <a href="mailto:contact@glaseditionslab.com" className="text-primary hover:underline">contact@glaseditionslab.com</a></li>
                <li><strong>TVA :</strong> Non assujetti (Article 293 B du CGI)</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 3 - Services et tarifs</h2>
            <p>GlasEditionsLab propose les services suivants :</p>
            
            <h3 className="font-semibold text-lg mt-6 mb-3">3.1 Abonnements mensuels</h3>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-stone-200 mt-4">
                <thead>
                  <tr className="bg-stone-50">
                    <th className="border border-stone-200 p-3 text-left">Plan</th>
                    <th className="border border-stone-200 p-3 text-left">Prix TTC</th>
                    <th className="border border-stone-200 p-3 text-left">Livres/mois</th>
                    <th className="border border-stone-200 p-3 text-left">Chapitres/livre</th>
                    <th className="border border-stone-200 p-3 text-left">Couvertures IA</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="border border-stone-200 p-3">Débutant</td>
                    <td className="border border-stone-200 p-3">27,00 €/mois</td>
                    <td className="border border-stone-200 p-3">3</td>
                    <td className="border border-stone-200 p-3">15 max</td>
                    <td className="border border-stone-200 p-3">Non</td>
                  </tr>
                  <tr className="bg-stone-50">
                    <td className="border border-stone-200 p-3">Auteur</td>
                    <td className="border border-stone-200 p-3">57,00 €/mois</td>
                    <td className="border border-stone-200 p-3">7</td>
                    <td className="border border-stone-200 p-3">30 max</td>
                    <td className="border border-stone-200 p-3">Oui</td>
                  </tr>
                  <tr>
                    <td className="border border-stone-200 p-3">Écrivain</td>
                    <td className="border border-stone-200 p-3">97,00 €/mois</td>
                    <td className="border border-stone-200 p-3">Illimité</td>
                    <td className="border border-stone-200 p-3">50 max</td>
                    <td className="border border-stone-200 p-3">Oui</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <h3 className="font-semibold text-lg mt-6 mb-3">3.2 Achat à l'unité</h3>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>Livre unique :</strong> 9,90 € TTC - 1 livre, jusqu'à 12 chapitres</li>
            </ul>

            <p className="mt-4">
              Les prix sont indiqués en euros toutes taxes comprises (TTC). EI Glas25 se 
              réserve le droit de modifier ses prix à tout moment. Toutefois, les services 
              seront facturés sur la base des tarifs en vigueur au moment de la validation 
              de la commande.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 4 - Commande et paiement</h2>
            
            <h3 className="font-semibold text-lg mt-4 mb-3">4.1 Processus de commande</h3>
            <p>Pour passer commande, le Client doit :</p>
            <ol className="list-decimal pl-6 space-y-2 mt-4">
              <li>Créer un compte ou se connecter à son compte existant</li>
              <li>Sélectionner le plan ou le service souhaité</li>
              <li>Valider son panier et accepter les présentes CGV</li>
              <li>Procéder au paiement sécurisé via Stripe</li>
            </ol>

            <h3 className="font-semibold text-lg mt-6 mb-3">4.2 Moyens de paiement</h3>
            <p>Les paiements sont effectués via la plateforme sécurisée Stripe, qui accepte :</p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>Cartes bancaires (Visa, Mastercard, American Express)</li>
              <li>Prélèvement SEPA (pour les abonnements)</li>
            </ul>
            <p className="mt-4">
              Le paiement est dû immédiatement à la commande. Pour les abonnements, le 
              renouvellement s'effectue automatiquement à chaque échéance mensuelle.
            </p>

            <h3 className="font-semibold text-lg mt-6 mb-3">4.3 Sécurité des paiements</h3>
            <p>
              Toutes les transactions sont sécurisées par Stripe, certifié PCI-DSS niveau 1. 
              EI Glas25 n'a jamais accès aux informations bancaires du Client.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 5 - Livraison et accès aux services</h2>
            <p>
              L'accès aux services est immédiat après validation du paiement. Le Client reçoit 
              une confirmation par email et peut immédiatement utiliser les fonctionnalités 
              correspondant à son plan.
            </p>
            <p className="mt-4">
              En cas de problème technique empêchant l'accès aux services, le Client est 
              invité à contacter le support à l'adresse : 
              <a href="mailto:contact@glaseditionslab.com" className="text-primary hover:underline ml-1">contact@glaseditionslab.com</a>
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 6 - Droit de rétractation</h2>
            <p>
              Conformément à l'article L221-18 du Code de la consommation, le Client dispose 
              d'un délai de <strong>14 jours</strong> à compter de la souscription pour exercer 
              son droit de rétractation, sans avoir à justifier de motifs ni à payer de pénalités.
            </p>
            
            <h3 className="font-semibold text-lg mt-6 mb-3">6.1 Exceptions au droit de rétractation</h3>
            <p>
              Conformément à l'article L221-28 du Code de la consommation, le droit de 
              rétractation ne peut pas être exercé pour :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>
                Les contenus numériques non fournis sur support matériel dont l'exécution a 
                commencé avec l'accord préalable du consommateur et pour lesquels il a renoncé 
                à son droit de rétractation
              </li>
              <li>
                Les services pleinement exécutés avant la fin du délai de rétractation et dont 
                l'exécution a commencé après accord préalable du consommateur
              </li>
            </ul>
            <p className="mt-4">
              <strong>En pratique :</strong> Si le Client a généré un livre ou utilisé le 
              service de manière significative, le droit de rétractation ne pourra plus être 
              exercé pour cette commande.
            </p>

            <h3 className="font-semibold text-lg mt-6 mb-3">6.2 Exercice du droit de rétractation</h3>
            <p>
              Pour exercer son droit de rétractation, le Client doit notifier sa décision par 
              email à <a href="mailto:contact@glaseditionslab.com" className="text-primary hover:underline">contact@glaseditionslab.com</a> en 
              indiquant clairement sa volonté de se rétracter, accompagnée de :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>Nom et prénom</li>
              <li>Email du compte</li>
              <li>Date de la commande</li>
              <li>Numéro de transaction (si disponible)</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 7 - Remboursement</h2>
            
            <h3 className="font-semibold text-lg mt-4 mb-3">7.1 Conditions de remboursement</h3>
            <p>En cas de rétractation valide, le remboursement sera effectué :</p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>Dans un délai de 14 jours à compter de la réception de la demande</li>
              <li>Par le même moyen de paiement que celui utilisé pour la commande</li>
              <li>Sans frais supplémentaires pour le Client</li>
            </ul>

            <h3 className="font-semibold text-lg mt-6 mb-3">7.2 Remboursement partiel</h3>
            <p>
              Pour les abonnements, si le Client a utilisé partiellement le service, un 
              remboursement au prorata pourra être calculé en fonction de l'utilisation 
              effective.
            </p>

            <h3 className="font-semibold text-lg mt-6 mb-3">7.3 Aucun remboursement</h3>
            <p>Aucun remboursement ne sera accordé dans les cas suivants :</p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>Délai de rétractation dépassé</li>
              <li>Services entièrement consommés</li>
              <li>Non-respect des CGU ayant entraîné une suspension de compte</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 8 - Résiliation d'abonnement</h2>
            <p>
              Le Client peut résilier son abonnement à tout moment depuis son espace client 
              ou par email. La résiliation prend effet à la fin de la période en cours, et 
              le Client conserve l'accès aux services jusqu'à cette date.
            </p>
            <p className="mt-4">
              En cas de résiliation, aucun remboursement ne sera effectué pour la période 
              restante déjà facturée, sauf exercice du droit de rétractation dans les 14 
              premiers jours.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 9 - Propriété des contenus</h2>
            <p>
              Le Client reste propriétaire de tous les contenus générés via le service 
              (livres, textes, images). Il dispose des droits d'exploitation complets et 
              peut utiliser ces contenus à des fins personnelles ou commerciales.
            </p>
            <p className="mt-4">
              EI Glas25 ne revendique aucun droit sur les créations du Client.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 10 - Responsabilité et garanties</h2>
            <p>
              EI Glas25 s'engage à fournir un service de qualité mais ne peut garantir que 
              le service sera exempt d'interruptions ou d'erreurs. Les contenus générés par 
              l'intelligence artificielle peuvent contenir des imperfections.
            </p>
            <p className="mt-4">
              La responsabilité de EI Glas25 ne saurait être engagée pour les dommages 
              indirects résultant de l'utilisation du service, notamment :
            </p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li>Perte de profits ou d'opportunités commerciales</li>
              <li>Atteinte à la réputation</li>
              <li>Perte de données</li>
              <li>Utilisation non conforme des contenus générés</li>
            </ul>
            <p className="mt-4">
              En tout état de cause, la responsabilité de EI Glas25 est limitée au montant 
              payé par le Client pour le service concerné.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 11 - Protection des données</h2>
            <p>
              Le traitement des données personnelles est détaillé dans notre{" "}
              <Link to="/privacy" className="text-primary hover:underline">
                Politique de Confidentialité
              </Link>.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 12 - Service client</h2>
            <p>Pour toute question ou réclamation, le Client peut contacter le service client :</p>
            <ul className="list-disc pl-6 space-y-2 mt-4">
              <li><strong>Email :</strong> <a href="mailto:contact@glaseditionslab.com" className="text-primary hover:underline">contact@glaseditionslab.com</a></li>
              <li><strong>Délai de réponse :</strong> 48 heures ouvrées maximum</li>
            </ul>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 13 - Médiation</h2>
            <p>
              En cas de litige, le Client peut recourir gratuitement au service de médiation 
              de la consommation. Le médiateur compétent est :
            </p>
            <div className="bg-stone-50 p-6 rounded-sm mt-4">
              <p><strong>Médiation de la consommation</strong></p>
              <p className="mt-2">
                Plateforme européenne de règlement en ligne des litiges :{" "}
                <a href="https://ec.europa.eu/consumers/odr" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                  https://ec.europa.eu/consumers/odr
                </a>
              </p>
            </div>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 14 - Modification des CGV</h2>
            <p>
              EI Glas25 se réserve le droit de modifier les présentes CGV à tout moment. Les 
              modifications entrent en vigueur dès leur publication sur le site. Les commandes 
              passées avant la modification restent soumises aux CGV en vigueur au moment de 
              la commande.
            </p>
          </section>

          <section>
            <h2 className="font-serif text-2xl font-semibold mb-4">Article 15 - Droit applicable</h2>
            <p>
              Les présentes CGV sont soumises au droit français. En cas de litige, et après 
              échec de toute tentative de résolution amiable, les tribunaux français seront 
              seuls compétents.
            </p>
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
