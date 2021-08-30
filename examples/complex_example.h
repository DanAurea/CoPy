/**
 * @enum cardinal engine.h
 */
typedef enum{north, east, south, west}cardinal; /**< Liste des directions */

/**
 * @enum unitName engine.h
 */
typedef enum{empty, decors, knight, scout, assassin, cleric, pyromancer, enchantress,
            dragonborn, darkWitch, lightningTotem, barrierTotem, mudGolem, golemAmbusher,
            frostGolem, stoneGolem, dragonTyrant, berserker, beastRider, poisonWisp, furgon}unitName; /**< Liste énumérée des noms d'unité */

/**
 * @enum unitEffect engine.h
 */
typedef enum{none, POWER_BONUS, ARMOR_BONUS, BARRIER, POISON, PARALYSE, FOCUS}unitEffect; /**< Représentation des différents status */

/**
 * @struct targetStat engine.h
 * Représente les informations liées aux cibles
 */
typedef struct{
    short vertRange; /**< Portée verticale */
    short horizRange;  /**< Portée horizontale */
    short ringSize;  /**< Taille de l'anneau */
    short line; /**< Ciblage en ligne */
}targetStat;

/**
 * @struct unitStat engine.h
 * Représente les statistiques d'une unité
 */
typedef struct{
    int HP; /**< Points de vie */
    int POWER; /**< Puissance */
    float ARMOR; /**< Armure */
    int RECOVERY; /**< Repos */
    float BLOCK[3]; /**< Blocage */
    targetStat target; /**< Ciblage */
    int MOVE_RANGE; /**< Portée mouvement */
}unitStat;

/**
 * @struct vector engine.h
 * Représente les coordonnées d'un vecteur
 */
typedef struct{
    int x; /**< Position x */
    int y; /**< Position y */
}vector; 

/**
 * @struct unit engine.h
 * Représente une unité
 */
typedef struct{
    unitName name; /**< Nom de l'unité */
    unitStat stat; /**< Statistiques de l'unité */
    unitEffect effect[NB_MAX_EFFECT]; /**< Effets sur l'unité*/
    cardinal direct; /**< Direction de l'unité */
    int noPlayer; /**< Propriétaire de l'unité */
    int unitColor; /**< Couleur de l'unité */
}unit;