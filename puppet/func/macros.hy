

(defmacro intent [&rest patterns]
  `(do
     (import [puppet.nlu.word_regex [Intent Pattern WordsRegex WILDCARD AnyWords]])
     (setv $ AnyWords)
     (Intent ~@(map (fn [p]
                      `(Pattern ~@(map (fn [pe]
                                         (if
                                           (= pe '*) 'WILDCARD
                                           pe))
                                       p)))
                    patterns))))

(defmacro intentn [name &rest patterns]
  `(setv ~name (intent ~@patterns)))

(defmacro say [line]
  `(await (.say state ~line)))

(defmacro lobby [user_input &rest branches]
  (or branches
      (return))

  `(if ~@(reduce + (gfor
                     branch branches
                     (if
                       (not (and (is (type branch) hy.HyList) branch))
                       (macro-error branch "each cond branch nexeds to be a nonempty list")
                       (= (len branch) 1) (do
                                            (setv g (gensym))
                                            [`(do (setv ~g ~(first branch)) ~g) g])
                       True
                       [`(~(first branch) ~user_input) `(do ~@(cut branch 1))])))))

(defmacro story [name &rest story-lines]
  `(defn/a ~name [state]
     ~@(reduce + (gfor line-lobby story-lines
                       `[(say ~(first line-lobby))
                         (setv user_input (await (.user_input state)))
                         (lobby user_input ~@(cut line-lobby 1))]))))

